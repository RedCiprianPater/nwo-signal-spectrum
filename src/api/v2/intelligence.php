<?php
/**
 * Unified Intelligence API v2
 * Combines Osiris OSINT data with Spectrum RF analysis
 */

require_once __DIR__ . '/../../../vendor/autoload.php';

use NWOSignalSpectrum\Services\OsirisFlightFeed;
use NWOSignalSpectrum\Services\OsirisCCTVFeed;
use NWOSignalSpectrum\Services\UnifiedIntelligence;
use NWOSignalSpectrum\Auth\Web3Auth;

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Authentication
$auth = new Web3Auth();
try {
    $auth->verifyRequest();
} catch (Exception $e) {
    http_response_code(401);
    echo json_encode(['error' => 'Unauthorized', 'message' => $e->getMessage()]);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$pathParts = explode('/', trim($path, '/'));
$endpoint = end($pathParts);

try {
    $intelligence = new UnifiedIntelligence();
    
    switch ($endpoint) {
        case 'all':
            // GET /api/v2/intelligence/all
            $region = $_GET['region'] ?? 'global';
            $severity = $_GET['severity'] ?? 'all';
            
            $data = $intelligence->getAllIntelligence([
                'region' => $region,
                'severity' => $severity,
                'include_osiris' => true,
                'include_spectrum' => true
            ]);
            
            echo json_encode([
                'timestamp' => date('c'),
                'region' => $region,
                'sources' => [
                    'flights' => [
                        'count' => $data['flights']['count'] ?? 0,
                        'anomalies' => $data['flights']['anomalies'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'rf_signals' => [
                        'count' => $data['rf_signals']['count'] ?? 0,
                        'anomalies' => $data['rf_signals']['anomalies'] ?? 0,
                        'source' => 'spectrum'
                    ],
                    'earthquakes' => [
                        'count' => $data['earthquakes']['count'] ?? 0,
                        'max_magnitude' => $data['earthquakes']['max_magnitude'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'fires' => [
                        'count' => $data['fires']['count'] ?? 0,
                        'total_area_km2' => $data['fires']['area'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'cctv' => [
                        'active' => $data['cctv']['active'] ?? 0,
                        'alerts' => $data['cctv']['alerts'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'maritime' => [
                        'vessels' => $data['maritime']['vessels'] ?? 0,
                        'anomalies' => $data['maritime']['anomalies'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'space_weather' => [
                        'kp_index' => $data['space']['kp_index'] ?? 0,
                        'alerts' => $data['space']['alerts'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'cyber_threats' => [
                        'cves' => $data['cyber']['cves'] ?? 0,
                        'critical' => $data['cyber']['critical'] ?? 0,
                        'source' => 'osiris'
                    ],
                    'conflict_zones' => [
                        'active' => $data['conflict']['active'] ?? 0,
                        'severity' => $data['conflict']['severity'] ?? 'low',
                        'source' => 'osiris'
                    ]
                ],
                'apocalypse_level' => $data['apocalypse_level'] ?? 0,
                'agent_consensus' => [
                    'online' => $data['agents']['online'] ?? 0,
                    'voting' => $data['agents']['voting'] ?? 0
                ]
            ]);
            break;
            
        case 'threats':
            // GET /api/v2/intelligence/threats
            $hours = intval($_GET['hours'] ?? 24);
            $minSeverity = $_GET['min_severity'] ?? 'medium';
            
            $threats = $intelligence->getUnifiedThreats([
                'hours' => $hours,
                'min_severity' => $minSeverity
            ]);
            
            echo json_encode([
                'timestamp' => date('c'),
                'time_range_hours' => $hours,
                'threats' => $threats,
                'total_count' => count($threats)
            ]);
            break;
            
        case 'map':
            // GET /api/v2/intelligence/map - GeoJSON for map display
            $bounds = $_GET['bounds'] ?? null; // sw_lat,sw_lng,ne_lat,ne_lng
            $layers = $_GET['layers'] ?? 'all';
            
            $geojson = $intelligence->getMapData([
                'bounds' => $bounds,
                'layers' => explode(',', $layers)
            ]);
            
            echo json_encode($geojson);
            break;
            
        default:
            http_response_code(404);
            echo json_encode(['error' => 'Endpoint not found']);
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Internal server error',
        'message' => $e->getMessage()
    ]);
}
