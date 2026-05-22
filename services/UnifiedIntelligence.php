<?php
/**
 * Unified Intelligence Service
 * Combines data from Osiris and Spectrum into unified views
 */

namespace NWOSignalSpectrum\Services;

use NWOSignalSpectrum\Database\Database;
use NWOSignalSpectrum\AgentNetwork\AgentNetwork;

class UnifiedIntelligence
{
    private Database $db;
    private OsirisFlightFeed $flightFeed;
    private OsirisCCTVFeed $cctvFeed;
    private AgentNetwork $agentNetwork;
    
    public function __construct()
    {
        $this->db = Database::getInstance();
        $this->flightFeed = new OsirisFlightFeed(
            $_ENV['OSIRIS_API_URL'] ?? 'http://localhost:3000'
        );
        $this->cctvFeed = new OsirisCCTVFeed(
            $_ENV['OSIRIS_API_URL'] ?? 'http://localhost:3000'
        );
        $this->agentNetwork = new AgentNetwork();
    }
    
    /**
     * Get all intelligence data combined
     */
    public function getAllIntelligence(array $filters = []): array
    {
        $region = $filters['region'] ?? 'global';
        
        // Fetch data in parallel where possible
        $data = [
            'flights' => $this->getFlightIntelligence($region),
            'rf_signals' => $this->getRFIntelligence($region),
            'earthquakes' => $this->getEarthquakeIntelligence($region),
            'fires' => $this->getFireIntelligence($region),
            'cctv' => $this->getCCTVIntelligence($region),
            'maritime' => $this->getMaritimeIntelligence($region),
            'space' => $this->getSpaceIntelligence(),
            'cyber' => $this->getCyberIntelligence(),
            'conflict' => $this->getConflictIntelligence($region),
            'agents' => $this->getAgentIntelligence()
        ];
        
        // Calculate unified apocalypse level
        $data['apocalypse_level'] = $this->calculateApocalypseLevel($data);
        
        return $data;
    }
    
    /**
     * Get unified threats from all sources
     */
    public function getUnifiedThreats(array $filters = []): array
    {
        $hours = $filters['hours'] ?? 24;
        $minSeverity = $filters['min_severity'] ?? 'low';
        
        $threats = [];
        
        // Get Osiris threats
        $flightAnomalies = $this->flightFeed->detectAnomalies($filters['region'] ?? 'global');
        foreach ($flightAnomalies as $anomaly) {
            $threats[] = [
                'id' => 'flight_' . md5(serialize($anomaly)),
                'source' => 'osiris',
                'category' => 'aviation',
                'type' => $anomaly['type'],
                'severity' => $anomaly['severity'],
                'title' => $this->getAnomalyTitle($anomaly),
                'description' => $this->getAnomalyDescription($anomaly),
                'location' => $anomaly['region'],
                'timestamp' => $anomaly['timestamp'],
                'metadata' => $anomaly
            ];
        }
        
        // Get Spectrum RF threats
        $rfThreats = $this->getRFThreats($filters);
        foreach ($rfThreats as $threat) {
            $threats[] = [
                'id' => 'rf_' . $threat['id'],
                'source' => 'spectrum',
                'category' => 'rf_anomaly',
                'type' => $threat['classification'],
                'severity' => $threat['anomaly_score'] > 3.0 ? 'high' : 'medium',
                'title' => "RF Anomaly: {$threat['classification']}",
                'description' => "Detected at {$threat['frequency_mhz']} MHz",
                'location' => $threat['location'],
                'timestamp' => $threat['timestamp'],
                'metadata' => $threat
            ];
        }
        
        // Filter by severity
        $severityOrder = ['low' => 1, 'medium' => 2, 'high' => 3, 'critical' => 4];
        $minLevel = $severityOrder[$minSeverity] ?? 1;
        
        $threats = array_filter($threats, function($t) use ($severityOrder, $minLevel) {
            return ($severityOrder[$t['severity']] ?? 0) >= $minLevel;
        });
        
        // Sort by severity and time
        usort($threats, function($a, $b) use ($severityOrder) {
            $sevDiff = ($severityOrder[$b['severity']] ?? 0) - ($severityOrder[$a['severity']] ?? 0);
            if ($sevDiff !== 0) return $sevDiff;
            return strtotime($b['timestamp']) - strtotime($a['timestamp']);
        });
        
        return array_values($threats);
    }
    
    /**
     * Report a new threat
     */
    public function reportThreat(array $data): string
    {
        $threatId = 'threat_' . uniqid();
        
        $this->db->insert('unified_threats', [
            'id' => $threatId,
            'source' => $data['source'],
            'category' => $data['category'],
            'severity' => $data['severity'],
            'title' => $data['title'],
            'description' => $data['description'],
            'location_lat' => $data['location']['lat'] ?? null,
            'location_lng' => $data['location']['lng'] ?? null,
            'metadata' => json_encode($data['metadata'] ?? []),
            'reported_by' => $data['reported_by'],
            'created_at' => date('Y-m-d H:i:s')
        ]);
        
        // Trigger agent consensus for high severity
        if (in_array($data['severity'], ['high', 'critical'])) {
            $this->agentNetwork->startConsensus([
                'type' => 'threat_assessment',
                'data' => ['threat_id' => $threatId],
                'timeout' => 300
            ]);
        }
        
        return $threatId;
    }
    
    /**
     * Get map data as GeoJSON
     */
    public function getMapData(array $filters = []): array
    {
        $features = [];
        $layers = $filters['layers'] ?? ['all'];
        
        if (in_array('all', $layers) || in_array('flights', $layers)) {
            $flights = $this->flightFeed->getFlights();
            foreach ($flights['flights'] ?? [] as $flight) {
                $features[] = [
                    'type' => 'Feature',
                    'geometry' => [
                        'type' => 'Point',
                        'coordinates' => [$flight['lon'], $flight['lat']]
                    ],
                    'properties' => [
                        'type' => 'flight',
                        'callsign' => $flight['callsign'],
                        'altitude' => $flight['altitude'],
                        'speed' => $flight['speed'],
                        'icon' => '✈️'
                    ]
                ];
            }
        }
        
        if (in_array('all', $layers) || in_array('rf_signals', $layers)) {
            $signals = $this->getRFIntelligence();
            foreach ($signals['signals'] ?? [] as $signal) {
                $features[] = [
                    'type' => 'Feature',
                    'geometry' => [
                        'type' => 'Point',
                        'coordinates' => [$signal['location']['lon'], $signal['location']['lat']]
                    ],
                    'properties' => [
                        'type' => 'rf_signal',
                        'frequency' => $signal['frequency_mhz'],
                        'classification' => $signal['classification'],
                        'strength' => $signal['strength'],
                        'icon' => '📡'
                    ]
                ];
            }
        }
        
        return [
            'type' => 'FeatureCollection',
            'features' => $features
        ];
    }
    
    // Private helper methods
    
    private function getFlightIntelligence(string $region): array
    {
        $flights = $this->flightFeed->getFlights(['region' => $region]);
        $anomalies = $this->flightFeed->detectAnomalies($region);
        
        return [
            'count' => count($flights['flights'] ?? []),
            'anomalies' => count($anomalies),
            'anomaly_details' => $anomalies
        ];
    }
    
    private function getRFIntelligence(string $region): array
    {
        // Query Spectrum database for recent signals
        $signals = $this->db->query(
            "SELECT * FROM spectrum_signals 
             WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
             AND location_lat IS NOT NULL
             ORDER BY signal_strength_dbm DESC
             LIMIT 50"
        );
        
        $anomalies = array_filter($signals, function($s) {
            return ($s['anomaly_score'] ?? 0) > 2.0;
        });
        
        return [
            'count' => count($signals),
            'anomalies' => count($anomalies),
            'signals' => $signals
        ];
    }
    
    private function getEarthquakeIntelligence(string $region): array
    {
        return ['count' => 0, 'max_magnitude' => 0];
    }
    
    private function getFireIntelligence(string $region): array
    {
        return ['count' => 0, 'area' => 0];
    }
    
    private function getCCTVIntelligence(string $region): array
    {
        $cctv = $this->cctvFeed->getActiveCameras($region);
        return [
            'active' => count($cctv),
            'alerts' => 0
        ];
    }
    
    private function getMaritimeIntelligence(string $region): array
    {
        return ['vessels' => 0, 'anomalies' => 0];
    }
    
    private function getSpaceIntelligence(): array
    {
        return ['kp_index' => 0, 'alerts' => 0];
    }
    
    private function getCyberIntelligence(): array
    {
        return ['cves' => 0, 'critical' => 0];
    }
    
    private function getConflictIntelligence(string $region): array
    {
        return ['active' => 0, 'severity' => 'low'];
    }
    
    private function getAgentIntelligence(): array
    {
        return $this->agentNetwork->getStatus();
    }
    
    private function calculateApocalypseLevel(array $data): int
    {
        $score = 0;
        
        // Flight anomalies
        if ($data['flights']['anomalies'] > 0) $score += 1;
        if ($data['flights']['anomalies'] > 3) $score += 1;
        
        // RF anomalies
        if ($data['rf_signals']['anomalies'] > 0) $score += 1;
        if ($data['rf_signals']['anomalies'] > 5) $score += 1;
        
        // Earthquakes
        if ($data['earthquakes']['max_magnitude'] > 6.0) $score += 2;
        if ($data['earthquakes']['max_magnitude'] > 7.0) $score += 2;
        
        // Space weather
        if ($data['space']['kp_index'] > 7) $score += 1;
        
        // Cyber threats
        if ($data['cyber']['critical'] > 0) $score += 1;
        if ($data['cyber']['critical'] > 5) $score += 1;
        
        // Conflict
        if ($data['conflict']['severity'] === 'high') $score += 2;
        if ($data['conflict']['severity'] === 'critical') $score += 3;
        
        return min(5, floor($score / 2));
    }
    
    private function getAnomalyTitle(array $anomaly): string
    {
        $titles = [
            'traffic_spike' => 'Aviation Traffic Spike',
            'military_concentration' => 'Military Aircraft Concentration',
            'elite_gathering' => 'Elite Gathering Detected'
        ];
        return $titles[$anomaly['type']] ?? 'Aviation Anomaly';
    }
    
    private function getAnomalyDescription(array $anomaly): string
    {
        switch ($anomaly['type']) {
            case 'traffic_spike':
                return "Traffic {$anomaly['multiplier']}x above baseline ({$anomaly['current_count']} flights)";
            case 'military_concentration':
                return "{$anomaly['military_count']} military aircraft detected in region";
            case 'elite_gathering':
                return "{$anomaly['private_jet_count']} private jets in area (possible elite event)";
            default:
                return 'Unusual aviation activity detected';
        }
    }
    
    private function getRFThreats(array $filters): array
    {
        // Query database for RF anomalies
        return $this->db->query(
            "SELECT *, frequency_hz/1000000 as frequency_mhz 
             FROM spectrum_signals 
             WHERE anomaly_score > 2.0 
             AND created_at > DATE_SUB(NOW(), INTERVAL ? HOUR)
             ORDER BY anomaly_score DESC
             LIMIT 20",
            [$filters['hours'] ?? 24]
        );
    }
}
