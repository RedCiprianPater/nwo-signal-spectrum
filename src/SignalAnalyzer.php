<?php
/**
 * Signal Analyzer Class
 * Handles spectrum analysis and signal detection
 */

namespace NWOSignalSpectrum;

class SignalAnalyzer {
    private $db;
    private $suscanPath;
    private $activeAnalyses = [];
    
    public function __construct() {
        $this->db = new \SQLite3(__DIR__ . '/../data/signals.db');
        $this->suscanPath = $_ENV['SUSCAN_PATH'] ?? '/usr/local/bin/suscan';
        $this->initDatabase();
    }
    
    private function initDatabase() {
        $this->db->exec('
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent TEXT,
                frequency_hz INTEGER,
                bandwidth_hz INTEGER,
                modulation TEXT,
                signal_strength_dbm REAL,
                confidence REAL,
                classification TEXT,
                metadata TEXT,
                raw_data BLOB
            );
            
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                status TEXT,
                agent TEXT,
                frequency_hz INTEGER,
                bandwidth_hz INTEGER,
                duration INTEGER,
                device TEXT,
                started_at DATETIME,
                completed_at DATETIME,
                results TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_signals_freq ON signals(frequency_hz);
            CREATE INDEX IF NOT EXISTS idx_signals_time ON signals(timestamp);
            CREATE INDEX IF NOT EXISTS idx_signals_agent ON signals(agent);
        ');
    }
    
    /**
     * Start a new spectrum analysis
     */
    public function startAnalysis(array $params): string {
        $analysisId = bin2hex(random_bytes(16));
        
        $stmt = $this->db->prepare('
            INSERT INTO analyses (id, status, agent, frequency_hz, bandwidth_hz, duration, device, started_at)
            VALUES (:id, :status, :agent, :freq, :bw, :duration, :device, datetime("now"))
        ');
        
        $stmt->bindValue(':id', $analysisId);
        $stmt->bindValue(':status', 'running');
        $stmt->bindValue(':agent', $params['agent'] ?? null);
        $stmt->bindValue(':freq', $params['frequency']);
        $stmt->bindValue(':bw', $params['bandwidth']);
        $stmt->bindValue(':duration', $params['duration']);
        $stmt->bindValue(':device', $params['device']);
        $stmt->execute();
        
        // Start analysis in background
        $this->runAnalysisAsync($analysisId, $params);
        
        return $analysisId;
    }
    
    /**
     * Run analysis asynchronously using suscan
     */
    private function runAnalysisAsync(string $analysisId, array $params) {
        $cmd = sprintf(
            '%s analyze --frequency %f --bandwidth %f --duration %d --device %s --output /tmp/analysis_%s.json 2>&1 &',
            escapeshellcmd($this->suscanPath),
            $params['frequency'],
            $params['bandwidth'],
            $params['duration'],
            escapeshellarg($params['device']),
            $analysisId
        );
        
        exec($cmd);
        
        // Store in active analyses
        $this->activeAnalyses[$analysisId] = [
            'params' => $params,
            'started' => time()
        ];
    }
    
    /**
     * Get detected signals with filters
     */
    public function getSignals(array $filters): array {
        $sql = 'SELECT * FROM signals WHERE 1=1';
        $params = [];
        
        if ($filters['frequency_min']) {
            $sql .= ' AND frequency_hz >= :freq_min';
            $params[':freq_min'] = $filters['frequency_min'];
        }
        
        if ($filters['frequency_max']) {
            $sql .= ' AND frequency_hz <= :freq_max';
            $params[':freq_max'] = $filters['frequency_max'];
        }
        
        if ($filters['modulation']) {
            $sql .= ' AND modulation = :modulation';
            $params[':modulation'] = $filters['modulation'];
        }
        
        if ($filters['agent']) {
            $sql .= ' AND agent = :agent';
            $params[':agent'] = $filters['agent'];
        }
        
        if ($filters['since']) {
            $sql .= ' AND timestamp >= :since';
            $params[':since'] = $filters['since'];
        }
        
        $sql .= ' ORDER BY timestamp DESC LIMIT :limit';
        $params[':limit'] = $filters['limit'];
        
        $stmt = $this->db->prepare($sql);
        foreach ($params as $key => $value) {
            $stmt->bindValue($key, $value);
        }
        
        $result = $stmt->execute();
        $signals = [];
        
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $row['metadata'] = json_decode($row['metadata'], true);
            $signals[] = $row;
        }
        
        return $signals;
    }
    
    /**
     * Get specific signal by ID
     */
    public function getSignal(string $signalId): ?array {
        $stmt = $this->db->prepare('SELECT * FROM signals WHERE id = :id');
        $stmt->bindValue(':id', $signalId);
        $result = $stmt->execute();
        
        $row = $result->fetchArray(SQLITE3_ASSOC);
        if ($row) {
            $row['metadata'] = json_decode($row['metadata'], true);
        }
        
        return $row ?: null;
    }
    
    /**
     * Decode a signal
     */
    public function decodeSignal(string $signalId, string $mode): array {
        $signal = $this->getSignal($signalId);
        
        if (!$signal) {
            throw new \Exception('Signal not found');
        }
        
        // Use suscan to decode
        $cmd = sprintf(
            '%s decode --input /tmp/signal_%s.raw --mode %s --output /tmp/decoded_%s.json 2>&1',
            escapeshellcmd($this->suscanPath),
            $signalId,
            escapeshellarg($mode),
            $signalId
        );
        
        exec($cmd, $output, $returnCode);
        
        if ($returnCode !== 0) {
            return [
                'success' => false,
                'error' => 'Decoding failed',
                'output' => implode("\n", $output)
            ];
        }
        
        $decodedFile = "/tmp/decoded_{$signalId}.json";
        if (file_exists($decodedFile)) {
            $decoded = json_decode(file_get_contents($decodedFile), true);
            unlink($decodedFile);
            return [
                'success' => true,
                'mode' => $mode,
                'data' => $decoded
            ];
        }
        
        return [
            'success' => false,
            'error' => 'No decoded output'
        ];
    }
    
    /**
     * List available SDR devices
     */
    public function listDevices(): array {
        $cmd = escapeshellcmd($this->suscanPath) . ' devices 2>&1';
        exec($cmd, $output, $returnCode);
        
        if ($returnCode !== 0) {
            // Return mock devices for testing
            return [
                ['id' => 'rtlsdr-0', 'name' => 'RTL-SDR V3', 'driver' => 'rtlsdr', 'available' => true],
                ['id' => 'hackrf-0', 'name' => 'HackRF One', 'driver' => 'hackrf', 'available' => false],
                ['id' => 'airspy-0', 'name' => 'Airspy Mini', 'driver' => 'airspy', 'available' => true]
            ];
        }
        
        $devices = [];
        foreach ($output as $line) {
            if (preg_match('/^(\S+)\s+(.+)$/', $line, $matches)) {
                $devices[] = [
                    'id' => $matches[1],
                    'name' => $matches[2],
                    'driver' => explode('-', $matches[1])[0],
                    'available' => true
                ];
            }
        }
        
        return $devices;
    }
    
    /**
     * Configure a device
     */
    public function configureDevice(string $deviceId, array $config): bool {
        // Store device configuration
        $configFile = __DIR__ . '/../config/devices/' . $deviceId . '.json';
        
        if (!is_dir(dirname($configFile))) {
            mkdir(dirname($configFile), 0755, true);
        }
        
        file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
        
        return true;
    }
    
    /**
     * Get device status
     */
    public function getDeviceStatus(string $deviceId): ?array {
        $configFile = __DIR__ . '/../config/devices/' . $deviceId . '.json';
        
        $config = [];
        if (file_exists($configFile)) {
            $config = json_decode(file_get_contents($configFile), true);
        }
        
        return [
            'id' => $deviceId,
            'connected' => true, // Would check actual device
            'config' => $config,
            'temperature' => 45.2, // Mock data
            'sample_rate' => $config['sample_rate'] ?? 2048000
        ];
    }
    
    /**
     * Store detected signal
     */
    public function storeSignal(array $signalData): string {
        $signalId = bin2hex(random_bytes(16));
        
        $stmt = $this->db->prepare('
            INSERT INTO signals (id, agent, frequency_hz, bandwidth_hz, modulation, 
                                signal_strength_dbm, confidence, classification, metadata)
            VALUES (:id, :agent, :freq, :bw, :mod, :strength, :confidence, :class, :meta)
        ');
        
        $stmt->bindValue(':id', $signalId);
        $stmt->bindValue(':agent', $signalData['agent'] ?? null);
        $stmt->bindValue(':freq', $signalData['frequency_hz']);
        $stmt->bindValue(':bw', $signalData['bandwidth_hz'] ?? 0);
        $stmt->bindValue(':mod', $signalData['modulation'] ?? 'unknown');
        $stmt->bindValue(':strength', $signalData['signal_strength_dbm'] ?? -100);
        $stmt->bindValue(':confidence', $signalData['confidence'] ?? 0.5);
        $stmt->bindValue(':class', $signalData['classification'] ?? 'unknown');
        $stmt->bindValue(':meta', json_encode($signalData['metadata'] ?? []));
        $stmt->execute();
        
        return $signalId;
    }
}
