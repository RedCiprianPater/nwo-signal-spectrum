<?php
/**
 * NWO Signal Spectrum - Apocalypse Indicators Integration
 * 
 * Adds apocalyptic signal types to the existing Signal Spectrum system
 * Sources: Aircraft, seismic, solar, radiation, asteroids, pandemics
 */

namespace NWOSignalSpectrum;

class ApocalypseIndicators {
    
    private $db;
    private $cache;
    
    // API Endpoints
    const USGS_EARTHQUAKE_API = 'https://earthquake.usgs.gov/fdsnws/event/1/query';
    const NASA_NEO_API = 'https://api.nasa.gov/neo/rest/v1/feed';
    const NOAA_SPACE_WEATHER = 'https://services.swpc.noaa.gov/products';
    const SAFECAST_API = 'https://api.safecast.org/measurements.json';
    const ADSB_EXCHANGE = 'https://api.adsbexchange.com/v2';
    const OPEN_METEO = 'https://api.open-meteo.com/v1';
    
    // Anomaly thresholds
    const THRESHOLDS = [
        'aircraft_spike' => 3.0,      // 3x normal activity
        'earthquake_cluster' => 3,     // 3+ M6+ in 24h
        'solar_flare_x_class' => 1,    // Any X-class flare
        'radiation_spike' => 10.0,     // 10x baseline
        'asteroid_close_approach' => 5, // <5 lunar distances
        'geomagnetic_storm' => 7,      // Kp index >= 7
    ];
    
    public function __construct($database, $cache = null) {
        $this->db = $database;
        $this->cache = $cache;
    }
    
    /**
     * Detect aviation anomalies (rich people fleeing)
     * Tracks private jet spikes from specific locations
     */
    public function detectAviationAnomaly($region = null) {
        // Query ADS-B data for business jet activity
        $params = [
            'format' => 'json',
            'filter' => 'bizjets', // Filter for business jets
        ];
        
        if ($region) {
            $params['bounds'] = $this->getRegionBounds($region);
        }
        
        $data = $this->fetch(self::ADSB_EXCHANGE . '/feed', $params);
        
        if (!$data || !isset($data['ac'])) {
            return null;
        }
        
        $currentCount = count($data['ac']);
        $baseline = $this->getHistoricalBaseline('aviation', $region, 168); // 7 days
        
        if ($baseline == 0) $baseline = 1;
        
        $anomalyScore = $currentCount / $baseline;
        
        if ($anomalyScore >= self::THRESHOLDS['aircraft_spike']) {
            return [
                'type' => 'aviation_anomaly',
                'severity' => $this->calculateSeverity($anomalyScore, self::THRESHOLDS['aircraft_spike']),
                'current_count' => $currentCount,
                'baseline' => $baseline,
                'anomaly_score' => $anomalyScore,
                'region' => $region,
                'timestamp' => time(),
                'description' => sprintf(
                    'Unusual spike in business jet activity: %d aircraft (%.1fx normal)',
                    $currentCount,
                    $anomalyScore
                )
            ];
        }
        
        return null;
    }
    
    /**
     * Monitor seismic activity for earthquake clusters
     */
    public function detectSeismicAnomaly($hours = 24) {
        $params = [
            'format' => 'geojson',
            'starttime' => date('Y-m-d\TH:i:s', strtotime("-{$hours} hours")),
            'minmagnitude' => 6.0,
            'orderby' => 'time',
        ];
        
        $data = $this->fetch(self::USGS_EARTHQUAKE_API, $params);
        
        if (!$data || !isset($data['features'])) {
            return null;
        }
        
        $significantQuakes = $data['features'];
        $count = count($significantQuakes);
        
        // Check for clustering (multiple large quakes in short timeframe)
        if ($count >= self::THRESHOLDS['earthquake_cluster']) {
            $maxMagnitude = 0;
            $locations = [];
            
            foreach ($significantQuakes as $quake) {
                $mag = $quake['properties']['mag'];
                $place = $quake['properties']['place'];
                
                if ($mag > $maxMagnitude) $maxMagnitude = $mag;
                $locations[] = $place;
            }
            
            return [
                'type' => 'seismic_cluster',
                'severity' => $maxMagnitude >= 7.0 ? 'critical' : 'high',
                'quake_count' => $count,
                'max_magnitude' => $maxMagnitude,
                'locations' => array_unique($locations),
                'timestamp' => time(),
                'description' => sprintf(
                    'Cluster of %d significant earthquakes detected (max M%.1f)',
                    $count,
                    $maxMagnitude
                )
            ];
        }
        
        return null;
    }
    
    /**
     * Monitor solar activity for dangerous flares/CMEs
     */
    public function detectSolarAnomaly() {
        // Get latest space weather data from NOAA
        $data = $this->fetch(self::NOAA_SPACE_WEATHER . '/noaa-planetary-k-index.json');
        $kpIndex = $this->getCurrentKpIndex($data);
        
        // Get X-ray flux for flare detection
        $xrayData = $this->fetch(self::NOAA_SPACE_WEATHER . '/goes-xray-flux-primary.json');
        $flareClass = $this->getFlareClass($xrayData);
        
        $anomalies = [];
        
        // Check for geomagnetic storm
        if ($kpIndex >= self::THRESHOLDS['geomagnetic_storm']) {
            $anomalies[] = [
                'type' => 'geomagnetic_storm',
                'severity' => $kpIndex >= 9 ? 'extreme' : ($kpIndex >= 8 ? 'severe' : 'strong'),
                'kp_index' => $kpIndex,
                'timestamp' => time(),
                'description' => "Geomagnetic storm in progress (Kp {$kpIndex})"
            ];
        }
        
        // Check for X-class solar flare
        if ($flareClass === 'X') {
            $anomalies[] = [
                'type' => 'solar_flare',
                'severity' => 'critical',
                'flare_class' => 'X',
                'timestamp' => time(),
                'description' => 'X-class solar flare detected - potential CME'
            ];
        }
        
        return count($anomalies) > 0 ? $anomalies : null;
    }
    
    /**
     * Monitor radiation levels globally
     */
    public function detectRadiationAnomaly() {
        // Get recent Safecast measurements
        $params = [
            'capture' => 'none',
            'per_page' => 1000,
            'since' => date('c', strtotime('-1 hour')),
        ];
        
        $data = $this->fetch(self::SAFECAST_API, $params);
        
        if (!$data || !isset($data['measurements'])) {
            return null;
        }
        
        $spikes = [];
        
        foreach ($data['measurements'] as $reading) {
            $value = $reading['value']; // μSv/h
            $location = $reading['location_name'] ?? 'Unknown';
            $baseline = $this->getRadiationBaseline($location);
            
            if ($baseline > 0 && ($value / $baseline) >= self::THRESHOLDS['radiation_spike']) {
                $spikes[] = [
                    'location' => $location,
                    'value' => $value,
                    'baseline' => $baseline,
                    'multiplier' => $value / $baseline
                ];
            }
        }
        
        if (count($spikes) >= 3) { // Multiple locations spiking
            return [
                'type' => 'radiation_spike',
                'severity' => 'critical',
                'spike_count' => count($spikes),
                'locations' => array_column($spikes, 'location'),
                'timestamp' => time(),
                'description' => sprintf(
                    'Radiation spikes detected at %d locations',
                    count($spikes)
                )
            ];
        }
        
        return null;
    }
    
    /**
     * Monitor near-Earth objects for close approaches
     */
    public function detectAsteroidThreat($days = 7) {
        $apiKey = getenv('NASA_API_KEY') ?: 'DEMO_KEY';
        
        $params = [
            'start_date' => date('Y-m-d'),
            'end_date' => date('Y-m-d', strtotime("+{$days} days")),
            'api_key' => $apiKey,
        ];
        
        $data = $this->fetch(self::NASA_NEO_API, $params);
        
        if (!$data || !isset($data['near_earth_objects'])) {
            return null;
        }
        
        $threats = [];
        $lunarDistance = 384400; // km
        
        foreach ($data['near_earth_objects'] as $date => $objects) {
            foreach ($objects as $neo) {
                $distance = $neo['close_approach_data'][0]['miss_distance']['kilometers'] ?? null;
                $diameter = $neo['estimated_diameter']['meters']['estimated_diameter_max'] ?? 0;
                $isHazardous = $neo['is_potentially_hazardous_asteroid'] ?? false;
                
                if ($distance && ($distance / $lunarDistance) <= self::THRESHOLDS['asteroid_close_approach']) {
                    if ($isHazardous || $diameter > 100) {
                        $threats[] = [
                            'name' => $neo['name'],
                            'diameter_m' => $diameter,
                            'distance_km' => (float)$distance,
                            'distance_ld' => (float)$distance / $lunarDistance,
                            'approach_date' => $date,
                            'is_hazardous' => $isHazardous
                        ];
                    }
                }
            }
        }
        
        if (count($threats) > 0) {
            usort($threats, function($a, $b) {
                return $a['distance_ld'] <=> $b['distance_ld'];
            });
            
            $closest = $threats[0];
            
            return [
                'type' => 'asteroid_close_approach',
                'severity' => $closest['is_hazardous'] ? 'critical' : 'high',
                'object_count' => count($threats),
                'closest_object' => $closest['name'],
                'closest_distance_ld' => round($closest['distance_ld'], 2),
                'diameter_m' => $closest['diameter_m'],
                'approach_date' => $closest['approach_date'],
                'timestamp' => time(),
                'description' => sprintf(
                    '%s approaching within %.1f lunar distances (%.0f m diameter)',
                    $closest['name'],
                    $closest['distance_ld'],
                    $closest['diameter_m']
                )
            ];
        }
        
        return null;
    }
    
    /**
     * Run all apocalypse indicators
     */
    public function runAllChecks() {
        $alerts = [];
        
        // Run all detection methods
        $checks = [
            'aviation' => $this->detectAviationAnomaly(),
            'seismic' => $this->detectSeismicAnomaly(),
            'solar' => $this->detectSolarAnomaly(),
            'radiation' => $this->detectRadiationAnomaly(),
            'asteroid' => $this->detectAsteroidThreat(),
        ];
        
        foreach ($checks as $type => $result) {
            if ($result) {
                if (is_array($result) && isset($result[0])) {
                    // Multiple anomalies from one check
                    foreach ($result as $anomaly) {
                        $alerts[] = $anomaly;
                        $this->storeSignal($anomaly);
                    }
                } else {
                    $alerts[] = $result;
                    $this->storeSignal($result);
                }
            }
        }
        
        return $alerts;
    }
    
    /**
     * Store detected signal in database
     */
    private function storeSignal($signal) {
        $stmt = $this->db->prepare("
            INSERT INTO apocalypse_signals 
            (type, severity, description, metadata, created_at)
            VALUES (?, ?, ?, ?, NOW())
        ");
        
        $metadata = json_encode([
            'current_count' => $signal['current_count'] ?? null,
            'baseline' => $signal['baseline'] ?? null,
            'anomaly_score' => $signal['anomaly_score'] ?? null,
            'max_magnitude' => $signal['max_magnitude'] ?? null,
            'kp_index' => $signal['kp_index'] ?? null,
            'distance_ld' => $signal['closest_distance_ld'] ?? null,
        ]);
        
        $stmt->execute([
            $signal['type'],
            $signal['severity'],
            $signal['description'],
            $metadata
        ]);
    }
    
    /**
     * Calculate apocalypse level (1-5) based on active signals
     */
    public function calculateApocalypseLevel() {
        $stmt = $this->db->query("
            SELECT severity, COUNT(*) as count 
            FROM apocalypse_signals 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY severity
        ");
        
        $scores = [
            'low' => 1,
            'medium' => 2,
            'high' => 3,
            'critical' => 4,
            'extreme' => 5
        ];
        
        $totalScore = 0;
        $maxSeverity = 0;
        
        while ($row = $stmt->fetch()) {
            $score = $scores[$row['severity']] ?? 1;
            $totalScore += $score * $row['count'];
            if ($score > $maxSeverity) $maxSeverity = $score;
        }
        
        // Level is max of: highest severity OR cumulative score threshold
        $level = max($maxSeverity, min(5, ceil($totalScore / 5)));
        
        return [
            'level' => $level,
            'description' => $this->getLevelDescription($level),
            'active_signals' => $totalScore,
            'timestamp' => time()
        ];
    }
    
    private function getLevelDescription($level) {
        $descriptions = [
            1 => 'Normal - No significant anomalies detected',
            2 => 'Elevated - Minor anomalies present',
            3 => 'High - Multiple concerning signals',
            4 => 'Severe - Critical conditions developing',
            5 => 'Extreme - Apocalyptic conditions possible'
        ];
        return $descriptions[$level] ?? 'Unknown';
    }
    
    // Helper methods
    private function fetch($url, $params = []) {
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200 || !$response) {
            return null;
        }
        
        return json_decode($response, true);
    }
    
    private function getHistoricalBaseline($type, $region, $hours) {
        // Query database for historical average
        $stmt = $this->db->prepare("
            SELECT AVG(value) as baseline 
            FROM signal_baselines 
            WHERE type = ? AND region = ? AND created_at > DATE_SUB(NOW(), INTERVAL ? HOUR)
        ");
        $stmt->execute([$type, $region, $hours]);
        $result = $stmt->fetch();
        return $result['baseline'] ?? 0;
    }
    
    private function getRadiationBaseline($location) {
        // Default baseline radiation ~0.1 μSv/h
        return 0.1;
    }
    
    private function getRegionBounds($region) {
        // Return lat/lon bounds for regions
        $bounds = [
            'davos' => [46.8, 47.0, 9.8, 10.0],
            'maui' => [20.5, 21.0, -156.5, -155.5],
            'monaco' => [43.7, 43.8, 7.4, 7.5],
        ];
        return $bounds[$region] ?? null;
    }
    
    private function calculateSeverity($score, $threshold) {
        $ratio = $score / $threshold;
        if ($ratio >= 10) return 'extreme';
        if ($ratio >= 5) return 'critical';
        if ($ratio >= 3) return 'high';
        if ($ratio >= 2) return 'medium';
        return 'low';
    }
    
    private function getCurrentKpIndex($data) {
        if (!$data || empty($data)) return 0;
        $latest = end($data);
        return isset($latest[1]) ? (int)$latest[1] : 0;
    }
    
    private function getFlareClass($data) {
        if (!$data || empty($data)) return null;
        // Parse X-ray flux and return flare class (A, B, C, M, X)
        $latest = end($data);
        $flux = isset($latest[1]) ? (float)$latest[1] : 0;
        
        if ($flux >= 1e-4) return 'X';
        if ($flux >= 1e-5) return 'M';
        if ($flux >= 1e-6) return 'C';
        if ($flux >= 1e-7) return 'B';
        return 'A';
    }
}
