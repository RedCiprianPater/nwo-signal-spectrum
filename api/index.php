<?php
/**
 * NWO Signal Spectrum - Complete API Router v2.1
 * 
 * Main entry point for all API endpoints
 * Includes RF signal analysis, agent network, apocalypse indicators
 * AND Osiris integration (v2 API)
 */

require_once __DIR__ . '/../vendor/autoload.php';

use NWOSignalSpectrum\SignalAnalyzer;
use NWOSignalSpectrum\AgentNetwork;
use NWOSignalSpectrum\Web3Auth;
use NWOSignalSpectrum\ApocalypseIndicators;

// CORS headers
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-NWO-Wallet, X-NWO-Signature, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Database connection
$db = new PDO(
    'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'),
    getenv('DB_USER'),
    getenv('DB_PASS'),
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

// Redis for real-time
$redis = new Redis();
$redis->connect(getenv('REDIS_HOST') ?: 'localhost', getenv('REDIS_PORT') ?: 6379);

// Router
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];
$pathParts = explode('/', trim($path, '/'));

// Remove 'api' from path
if ($pathParts[0] === 'api') array_shift($pathParts);

// Check for v1 or v2
$apiVersion = $pathParts[0] ?? 'v1';
if (in_array($pathParts[0], ['v1', 'v2'])) {
    array_shift($pathParts);
}

$endpoint = $pathParts[0] ?? '';
$action = $pathParts[1] ?? '';
$id = $pathParts[2] ?? null;

try {
    // Route to v2 handlers if version 2
    if ($apiVersion === 'v2') {
        handleV2Routes($method, $endpoint, $action, $id, $db, $redis);
    } else {
        // v1 routes (existing)
        handleV1Routes($method, $endpoint, $action, $id, $db, $redis);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}

// V2 Route Handler (NEW - Osiris Integration)
function handleV2Routes($method, $endpoint, $action, $id, $db, $redis) {
    switch ($endpoint) {
        // Unified Intelligence (NEW)
        case 'intelligence':
            require_once __DIR__ . '/v2/intelligence.php';
            break;
            
        // Unified Threats (NEW)
        case 'threats':
            require_once __DIR__ . '/v2/threats.php';
            break;
            
        // Cross-Platform Consensus (NEW)
        case 'agents':
        case 'consensus':
            require_once __DIR__ . '/v2/consensus.php';
            break;
            
        // Enhanced Apocalypse with Osiris data
        case 'apocalypse':
            handleV2Apocalypse($method, $action, $db);
            break;
            
        // Fallback to v1 for non-overridden endpoints
        default:
            handleV1Routes($method, $endpoint, $action, $id, $db, $redis);
    }
}

// V1 Route Handler (EXISTING - with your custom implementations)
function handleV1Routes($method, $endpoint, $action, $id, $db, $redis) {
    switch ($endpoint) {
        // Health check
        case 'health':
            handleHealth($db, $redis);
            break;
            
        // Authentication
        case 'auth':
            handleAuth($method, $db);
            break;
            
        // RF Signals
        case 'signals':
            handleSignals($method, $action, $id, $db, $redis);
            break;
            
        // Agent Network
        case 'agents':
            handleAgents($method, $action, $id, $db);
            break;
            
        case 'network':
            handleNetwork($method, $action, $db);
            break;
            
        // Apocalypse Indicators
        case 'apocalypse':
            handleApocalypse($method, $action, $db);
            break;
            
        // Spectrum Analysis
        case 'spectrum':
            handleSpectrum($method, $action, $db);
            break;
            
        // WebSocket token
        case 'ws-token':
            handleWsToken($method, $db);
            break;
            
        default:
            http_response_code(404);
            echo json_encode(['error' => 'Endpoint not found', 'version' => 'v1']);
    }
}

// V2 Apocalypse Handler (Enhanced with Osiris data)
function handleV2Apocalypse($method, $action, $db) {
    require_once __DIR__ . '/../services/UnifiedIntelligence.php';
    
    $intel = new NWOSignalSpectrum\Services\UnifiedIntelligence();
    
    if ($method === 'GET' && $action === 'unified') {
        // GET /api/v2/apocalypse/unified
        $data = $intel->getAllIntelligence();
        
        echo json_encode([
            'level' => $data['apocalypse_level'],
            'description' => getApocalypseDescription($data['apocalypse_level']),
            'active_signals' => $data['rf_signals']['count'] ?? 0,
            'breakdown' => [
                'aviation' => $data['flights']['anomalies'] ?? 0,
                'seismic' => $data['earthquakes']['count'] ?? 0,
                'solar' => $data['space']['alerts'] ?? 0,
                'radiation' => 0,
                'rf_anomaly' => $data['rf_signals']['anomalies'] ?? 0,
                'cyber' => $data['cyber']['critical'] ?? 0,
                'conflict' => $data['conflict']['active'] ?? 0
            ],
            'timestamp' => date('c')
        ]);
    } else {
        // Fallback to v1 handler
        handleApocalypse($method, $action, $db);
    }
}

function getApocalypseDescription($level) {
    $descriptions = [
        0 => 'Normal - No significant threats detected',
        1 => 'Elevated - Minor anomalies detected',
        2 => 'Moderate - Multiple concerning signals',
        3 => 'High - Significant threat activity',
        4 => 'Critical - Severe threats imminent',
        5 => 'Extinction - Catastrophic events in progress'
    ];
    return $descriptions[$level] ?? 'Unknown';
}

// Handler Functions (YOUR CUSTOM IMPLEMENTATIONS)

function handleHealth($db, $redis) {
    $health = [
        'status' => 'healthy',
        'version' => '2.1.0',
        'api_versions' => ['v1', 'v2'],
        'timestamp' => time(),
        'services' => [
            'database' => checkDatabase($db),
            'redis' => checkRedis($redis),
        ],
        'metrics' => [
            'signals_24h' => getSignalCount($db, 24),
            'agents_online' => getAgentCount($db),
            'apocalypse_level' => getCurrentApocalypseLevel($db)
        ]
    ];
    
    echo json_encode($health);
}

// YOUR CUSTOM handleAuth
function handleAuth($method, $db) {
    if ($method !== 'POST') {
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        return;
    }
    
    $data = json_decode(file_get_contents('php://input'), true);
    $wallet = $_SERVER['HTTP_X_NWO_WALLET'] ?? '';
    $signature = $_SERVER['HTTP_X_NWO_SIGNATURE'] ?? '';
    
    $auth = new Web3Auth($db);
    $result = $auth->authenticate($wallet, $signature, $data['message'] ?? '');
    
    if ($result['success']) {
        echo json_encode([
            'token' => $result['token'],
            'wallet' => $wallet,
            'expires' => $result['expires']
        ]);
    } else {
        http_response_code(401);
        echo json_encode(['error' => $result['error']]);
    }
}

// YOUR CUSTOM handleSignals
function handleSignals($method, $action, $id, $db, $redis) {
    $analyzer = new SignalAnalyzer($db, $redis);
    
    switch ($method) {
        case 'GET':
            if ($id) {
                // Get specific signal
                $signal = $analyzer->getSignal($id);
                echo json_encode($signal);
            } else {
                // List signals with filters
                $filters = [
                    'freq_min' => $_GET['freq_min'] ?? null,
                    'freq_max' => $_GET['freq_max'] ?? null,
                    'modulation' => $_GET['modulation'] ?? null,
                    'classification' => $_GET['classification'] ?? null,
                    'limit' => min(100, intval($_GET['limit'] ?? 50)),
                    'offset' => intval($_GET['offset'] ?? 0)
                ];
                
                $signals = $analyzer->getSignals($filters);
                echo json_encode([
                    'signals' => $signals,
                    'total' => $analyzer->getTotalCount($filters),
                    'limit' => $filters['limit'],
                    'offset' => $filters['offset']
                ]);
            }
            break;
            
        case 'POST':
            // Submit new signal
            $data = json_decode(file_get_contents('php://input'), true);
            $signalId = $analyzer->submitSignal($data);
            
            // Broadcast to WebSocket subscribers
            $redis->publish('signals', json_encode([
                'type' => 'new_signal',
                'id' => $signalId,
                'data' => $data
            ]));
            
            http_response_code(201);
            echo json_encode(['id' => $signalId, 'status' => 'submitted']);
            break;
            
        case 'PUT':
            // Update signal classification
            if (!$id) {
                http_response_code(400);
                echo json_encode(['error' => 'Signal ID required']);
                return;
            }
            
            $data = json_decode(file_get_contents('php://input'), true);
            $analyzer->updateClassification($id, $data);
            echo json_encode(['status' => 'updated']);
            break;
    }
}

// YOUR CUSTOM handleAgents
function handleAgents($method, $action, $id, $db) {
    $network = new AgentNetwork($db);
    
    switch ($method) {
        case 'GET':
            if ($action === 'online') {
                $agents = $network->getOnlineAgents();
                echo json_encode(['agents' => $agents]);
            } else {
                $agent = $network->getAgent($id);
                echo json_encode($agent);
            }
            break;
            
        case 'POST':
            $data = json_decode(file_get_contents('php://input'), true);
            $result = $network->registerAgent($data);
            echo json_encode(['agent_id' => $result]);
            break;
    }
}

// YOUR CUSTOM handleNetwork
function handleNetwork($method, $action, $db) {
    $network = new AgentNetwork($db);
    
    switch ($action) {
        case 'join':
            $data = json_decode(file_get_contents('php://input'), true);
            $result = $network->join($data['wallet']);
            echo json_encode(['status' => $result ? 'joined' : 'failed']);
            break;
            
        case 'tasks':
            if ($method === 'GET') {
                $tasks = $network->getTasks($_GET['status'] ?? null);
                echo json_encode(['tasks' => $tasks]);
            } else {
                $data = json_decode(file_get_contents('php://input'), true);
                $taskId = $network->submitTask($data);
                echo json_encode(['task_id' => $taskId]);
            }
            break;
            
        case 'vote':
            $data = json_decode(file_get_contents('php://input'), true);
            $result = $network->submitVote($data['task_id'], $data);
            echo json_encode(['consensus' => $result]);
            break;
            
        case 'consensus':
            $taskId = $_GET['task_id'] ?? '';
            $consensus = $network->getConsensus($taskId);
            echo json_encode($consensus);
            break;
    }
}

// YOUR COMPLETE CUSTOM handleApocalypse
function handleApocalypse($method, $action, $db) {
    $indicators = new ApocalypseIndicators($db);
    
    switch ($action) {
        case 'level':
            // Get current apocalypse level
            $level = $indicators->calculateApocalypseLevel();
            echo json_encode($level);
            break;
            
        case 'alerts':
            // Get active alerts
            $filters = [
                'severity' => $_GET['severity'] ?? null,
                'type' => $_GET['type'] ?? null,
                'hours' => intval($_GET['hours'] ?? 24),
                'limit' => min(100, intval($_GET['limit'] ?? 50))
            ];
            
            $alerts = $indicators->getAlerts($filters);
            echo json_encode([
                'alerts' => $alerts,
                'count' => count($alerts),
                'filters' => $filters
            ]);
            break;
            
        case 'check':
            // Run all checks (admin only)
            $alerts = $indicators->runAllChecks();
            echo json_encode([
                'checks_run' => 6,
                'alerts_found' => count($alerts),
                'alerts' => $alerts
            ]);
            break;
            
        case 'aviation':
            // Aviation anomaly check
            $region = $_GET['region'] ?? null;
            $anomaly = $indicators->detectAviationAnomaly($region);
            echo json_encode($anomaly ?: ['status' => 'no_anomaly']);
            break;
            
        case 'seismic':
            // Seismic monitoring
            $hours = intval($_GET['hours'] ?? 24);
            $seismic = $indicators->detectSeismicAnomaly($hours);
            echo json_encode($seismic ?: ['status' => 'no_anomaly']);
            break;
            
        case 'solar':
            // Solar activity
            $solar = $indicators->detectSolarAnomaly();
            echo json_encode($solar ?: ['status' => 'no_anomaly']);
            break;
            
        case 'radiation':
            // Radiation monitoring
            $radiation = $indicators->detectRadiationAnomaly();
            echo json_encode($radiation ?: ['status' => 'no_anomaly']);
            break;
            
        case 'asteroid':
            // Asteroid tracking
            $days = intval($_GET['days'] ?? 7);
            $asteroid = $indicators->detectAsteroidThreat($days);
            echo json_encode($asteroid ?: ['status' => 'no_threat']);
            break;
            
        case 'history':
            // Apocalypse level history
            $hours = intval($_GET['hours'] ?? 168); // 7 days default
            $history = $indicators->getLevelHistory($hours);
            echo json_encode([
                'history' => $history,
                'max_level' => max(array_column($history, 'level'))
            ]);
            break;
            
        default:
            // Dashboard summary
            $dashboard = [
                'level' => $indicators->calculateApocalypseLevel(),
                'active_alerts' => $indicators->getAlerts(['hours' => 24]),
                'stats' => [
                    'aviation_checks' => $indicators->getCheckCount('aviation'),
                    'seismic_events' => $indicators->getCheckCount('seismic'),
                    'solar_alerts' => $indicators->getCheckCount('solar'),
                    'radiation_spikes' => $indicators->getCheckCount('radiation'),
                    'asteroid_warnings' => $indicators->getCheckCount('asteroid')
                ]
            ];
            echo json_encode($dashboard);
    }
}

// YOUR CUSTOM handleSpectrum
function handleSpectrum($method, $action, $db) {
    $analyzer = new SignalAnalyzer($db);
    
    switch ($action) {
        case 'analyze':
            $data = json_decode(file_get_contents('php://input'), true);
            $result = $analyzer->analyzeSpectrum($data);
            echo json_encode($result);
            break;
            
        case 'share':
            $data = json_decode(file_get_contents('php://input'), true);
            $shareId = $analyzer->shareSignal($data['signal_id']);
            echo json_encode(['shared_id' => $shareId]);
            break;
            
        case 'frequency-bands':
            $bands = $analyzer->getFrequencyBands();
            echo json_encode(['bands' => $bands]);
            break;
    }
}

// YOUR CUSTOM handleWsToken
function handleWsToken($method, $db) {
    if ($method !== 'POST') {
        http_response_code(405);
        return;
    }
    
    $wallet = $_SERVER['HTTP_X_NWO_WALLET'] ?? '';
    
    // Generate WebSocket auth token
    $token = bin2hex(random_bytes(32));
    $expires = time() + 3600; // 1 hour
    
    $stmt = $db->prepare("
        INSERT INTO ws_tokens (token, wallet, expires_at)
        VALUES (?, ?, FROM_UNIXTIME(?))
    ");
    $stmt->execute([$token, $wallet, $expires]);
    
    echo json_encode([
        'token' => $token,
        'expires' => $expires,
        'ws_url' => 'wss://nwo.capital/ws/spectrum'
    ]);
}

// YOUR CUSTOM Helper functions

function checkDatabase($db) {
    try {
        $db->query('SELECT 1');
        return 'up';
    } catch (Exception $e) {
        return 'down';
    }
}

function checkRedis($redis) {
    try {
        return $redis->ping() ? 'up' : 'down';
    } catch (Exception $e) {
        return 'down';
    }
}

function getSignalCount($db, $hours) {
    $stmt = $db->prepare("
        SELECT COUNT(*) FROM signals 
        WHERE created_at > DATE_SUB(NOW(), INTERVAL ? HOUR)
    ");
    $stmt->execute([$hours]);
    return $stmt->fetchColumn();
}

function getAgentCount($db) {
    $stmt = $db->query("
        SELECT COUNT(*) FROM agents 
        WHERE last_seen > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
    ");
    return $stmt->fetchColumn();
}

function getCurrentApocalypseLevel($db) {
    $stmt = $db->query("
        SELECT level FROM apocalypse_level_history 
        ORDER BY recorded_at DESC LIMIT 1
    ");
    $result = $stmt->fetch();
    return $result ? intval($result['level']) : 1;
}
