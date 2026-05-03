<?php
/**
 * Agent Network Class
 * Handles signal sharing and consensus between agents
 */

namespace NWOSignalSpectrum;

class AgentNetwork {
    private $db;
    private $redis;
    
    public function __construct() {
        $this->db = new \SQLite3(__DIR__ . '/../data/signals.db');
        $this->initDatabase();
        
        // Try to connect to Redis for real-time updates
        try {
            $this->redis = new \Redis();
            $this->redis->connect('127.0.0.1', 6379);
        } catch (\Exception $e) {
            $this->redis = null;
        }
    }
    
    private function initDatabase() {
        $this->db->exec('
            CREATE TABLE IF NOT EXISTS shared_signals (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                signal_id TEXT,
                signal_data TEXT,
                signature TEXT
            );
            
            CREATE TABLE IF NOT EXISTS consensus_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                signal_id TEXT,
                classification TEXT,
                confidence REAL
            );
            
            CREATE INDEX IF NOT EXISTS idx_shared_agent ON shared_signals(agent);
            CREATE INDEX IF NOT EXISTS idx_shared_signal ON shared_signals(signal_id);
            CREATE INDEX IF NOT EXISTS idx_votes_signal ON consensus_votes(signal_id);
        ');
    }
    
    /**
     * Share signal with the network
     */
    public function shareSignal(string $agent, array $signalData): string {
        $sharedId = bin2hex(random_bytes(16));
        
        // Verify signal signature if provided
        $signature = $signalData['signature'] ?? '';
        $signalData['agent'] = $agent;
        
        $stmt = $this->db->prepare('
            INSERT INTO shared_signals (id, agent, signal_id, signal_data, signature)
            VALUES (:id, :agent, :signal_id, :data, :sig)
        ');
        
        $stmt->bindValue(':id', $sharedId);
        $stmt->bindValue(':agent', $agent);
        $stmt->bindValue(':signal_id', $signalData['signal_id'] ?? $sharedId);
        $stmt->bindValue(':data', json_encode($signalData));
        $stmt->bindValue(':sig', $signature);
        $stmt->execute();
        
        // Publish to Redis for real-time updates
        if ($this->redis) {
            $this->redis->publish('nwo:signals', json_encode([
                'type' => 'new_signal',
                'data' => $signalData
            ]));
        }
        
        // Broadcast to other agents via WebSocket or HTTP
        $this->broadcastToAgents($signalData);
        
        return $sharedId;
    }
    
    /**
     * Get signals from the entire network
     */
    public function getNetworkSignals(array $filters): array {
        $sql = '
            SELECT s.*, 
                   (SELECT COUNT(*) FROM consensus_votes WHERE signal_id = s.signal_id) as vote_count,
                   (SELECT classification FROM consensus_votes 
                    WHERE signal_id = s.signal_id 
                    GROUP BY classification 
                    ORDER BY COUNT(*) DESC LIMIT 1) as consensus_class
            FROM shared_signals s 
            WHERE 1=1
        ';
        
        $params = [];
        
        if ($filters['frequency_min'] || $filters['frequency_max']) {
            $sql .= ' AND (json_extract(s.signal_data, "$.frequency_hz") BETWEEN :freq_min AND :freq_max)';
            $params[':freq_min'] = $filters['frequency_min'] ?? 0;
            $params[':freq_max'] = $filters['frequency_max'] ?? 999999999999;
        }
        
        if ($filters['modulation']) {
            $sql .= ' AND json_extract(s.signal_data, "$.modulation") = :modulation';
            $params[':modulation'] = $filters['modulation'];
        }
        
        if ($filters['classification']) {
            $sql .= ' AND (SELECT classification FROM consensus_votes 
                          WHERE signal_id = s.signal_id 
                          GROUP BY classification 
                          ORDER BY COUNT(*) DESC LIMIT 1) = :class';
            $params[':class'] = $filters['classification'];
        }
        
        $sql .= ' ORDER BY s.timestamp DESC LIMIT :limit';
        $params[':limit'] = $filters['limit'];
        
        $stmt = $this->db->prepare($sql);
        foreach ($params as $key => $value) {
            $stmt->bindValue($key, $value);
        }
        
        $result = $stmt->execute();
        $signals = [];
        
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $signalData = json_decode($row['signal_data'], true);
            $signalData['shared_id'] = $row['id'];
            $signalData['shared_by'] = $row['agent'];
            $signalData['shared_at'] = $row['timestamp'];
            $signalData['vote_count'] = $row['vote_count'];
            $signalData['consensus_classification'] = $row['consensus_class'];
            $signals[] = $signalData;
        }
        
        return $signals;
    }
    
    /**
     * Submit consensus vote for signal classification
     */
    public function submitVote(string $agent, string $signalId, string $classification, float $confidence): array {
        // Record vote
        $stmt = $this->db->prepare('
            INSERT INTO consensus_votes (agent, signal_id, classification, confidence)
            VALUES (:agent, :signal_id, :class, :confidence)
        ');
        
        $stmt->bindValue(':agent', $agent);
        $stmt->bindValue(':signal_id', $signalId);
        $stmt->bindValue(':class', $classification);
        $stmt->bindValue(':confidence', $confidence);
        $stmt->execute();
        
        // Calculate consensus
        $consensus = $this->calculateConsensus($signalId);
        
        return [
            'signal_id' => $signalId,
            'your_vote' => [
                'classification' => $classification,
                'confidence' => $confidence
            ],
            'consensus' => $consensus,
            'total_votes' => $consensus['total_votes']
        ];
    }
    
    /**
     * Calculate consensus for a signal
     */
    private function calculateConsensus(string $signalId): array {
        $stmt = $this->db->prepare('
            SELECT classification, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM consensus_votes
            WHERE signal_id = :signal_id
            GROUP BY classification
            ORDER BY count DESC
        ');
        
        $stmt->bindValue(':signal_id', $signalId);
        $result = $stmt->execute();
        
        $votes = [];
        $totalVotes = 0;
        
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $votes[] = [
                'classification' => $row['classification'],
                'count' => $row['count'],
                'avg_confidence' => $row['avg_confidence']
            ];
            $totalVotes += $row['count'];
        }
        
        $consensusClass = $votes[0]['classification'] ?? 'unknown';
        $consensusConfidence = $votes[0]['avg_confidence'] ?? 0;
        
        return [
            'classification' => $consensusClass,
            'confidence' => $consensusConfidence,
            'total_votes' => $totalVotes,
            'breakdown' => $votes
        ];
    }
    
    /**
     * Broadcast signal to connected agents
     */
    private function broadcastToAgents(array $signalData) {
        // Get list of connected agents
        $agents = $this->getConnectedAgents();
        
        foreach ($agents as $agent) {
            // Send via HTTP POST to agent's webhook
            if ($agent['webhook_url']) {
                $this->sendToAgent($agent['webhook_url'], $signalData);
            }
        }
    }
    
    /**
     * Send signal data to agent webhook
     */
    private function sendToAgent(string $webhookUrl, array $signalData) {
        $ch = curl_init($webhookUrl);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($signalData));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_exec($ch);
        curl_close($ch);
    }
    
    /**
     * Get connected agents
     */
    private function getConnectedAgents(): array {
        // In production, this would query a registry or use WebSocket connections
        return [
            ['id' => 'agent-1', 'webhook_url' => 'http://agent1.nwo.local:8080/webhook'],
            ['id' => 'agent-2', 'webhook_url' => 'http://agent2.nwo.local:8080/webhook']
        ];
    }
    
    /**
     * Get agent reputation score
     */
    public function getAgentReputation(string $agent): array {
        // Calculate based on correct classifications vs consensus
        $stmt = $this->db->prepare('
            SELECT 
                COUNT(*) as total_votes,
                SUM(CASE WHEN v.classification = c.consensus THEN 1 ELSE 0 END) as correct_votes
            FROM consensus_votes v
            JOIN (
                SELECT signal_id, classification as consensus
                FROM consensus_votes
                GROUP BY signal_id
                ORDER BY COUNT(*) DESC
            ) c ON v.signal_id = c.signal_id
            WHERE v.agent = :agent
        ');
        
        $stmt->bindValue(':agent', $agent);
        $result = $stmt->execute();
        $row = $result->fetchArray(SQLITE3_ASSOC);
        
        $accuracy = $row['total_votes'] > 0 
            ? $row['correct_votes'] / $row['total_votes'] 
            : 0;
        
        return [
            'agent' => $agent,
            'total_votes' => $row['total_votes'],
            'correct_votes' => $row['correct_votes'],
            'accuracy' => $accuracy,
            'reputation_score' => $accuracy * 100
        ];
    }
}
