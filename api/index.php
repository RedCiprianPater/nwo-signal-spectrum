<?php
/**
 * NWO Signal Spectrum API
 * Main API endpoints for signal analysis and agent coordination
 */

require_once __DIR__ . '/../vendor/autoload.php';

use NWOSignalSpectrum\SignalAnalyzer;
use NWOSignalSpectrum\AgentNetwork;
use NWOSignalSpectrum\Web3Auth;

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-NWO-Wallet, X-NWO-Signature');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];
$input = json_decode(file_get_contents('php://input'), true) ?: [];

// Web3 Authentication
$auth = new Web3Auth();
$wallet = $_SERVER['HTTP_X_NWO_WALLET'] ?? $input['wallet'] ?? null;
$signature = $_SERVER['HTTP_X_NWO_SIGNATURE'] ?? $input['signature'] ?? null;

// Initialize components
$analyzer = new SignalAnalyzer();
$network = new AgentNetwork();

$response = ['status' => 'error', 'message' => 'Unknown endpoint'];
$code = 404;

try {
    switch ($path) {
        // Signal Analysis Endpoints
        case '/api/v1/analyze':
            if ($method === 'POST') {
                $frequency = $input['frequency'] ?? null;
                $bandwidth = $input['bandwidth'] ?? 2e6;
                $duration = $input['duration'] ?? 10;
                $device = $input['device'] ?? 'default';
                
                if (!$frequency) {
                    $response = ['status' => 'error', 'message' => 'Frequency required'];
                    $code = 400;
                } else {
                    $analysisId = $analyzer->startAnalysis([
                        'frequency' => $frequency,
                        'bandwidth' => $bandwidth,
                        'duration' => $duration,
                        'device' => $device,
                        'agent' => $wallet
                    ]);
                    
                    $response = [
                        'status' => 'success',
                        'analysis_id' => $analysisId,
                        'frequency' => $frequency,
                        'bandwidth' => $bandwidth,
                        'estimated_duration' => $duration
                    ];
                    $code = 200;
                }
            }
            break;

        case '/api/v1/signals':
            if ($method === 'GET') {
                $filters = [
                    'frequency_min' => $_GET['freq_min'] ?? null,
                    'frequency_max' => $_GET['freq_max'] ?? null,
                    'modulation' => $_GET['modulation'] ?? null,
                    'agent' => $_GET['agent'] ?? null,
                    'since' => $_GET['since'] ?? null,
                    'limit' => intval($_GET['limit'] ?? 50)
                ];
                
                $signals = $analyzer->getSignals($filters);
                
                $response = [
                    'status' => 'success',
                    'count' => count($signals),
                    'signals' => $signals
                ];
                $code = 200;
            }
            break;

        case '/api/v1/signals/' . (preg_match('/^\/api\/v1\/signals\/(.+)$/', $path, $matches) ? $matches[1] : ''):
            if ($method === 'GET' && isset($matches[1])) {
                $signalId = $matches[1];
                $signal = $analyzer->getSignal($signalId);
                
                if ($signal) {
                    $response = ['status' => 'success', 'signal' => $signal];
                    $code = 200;
                } else {
                    $response = ['status' => 'error', 'message' => 'Signal not found'];
                    $code = 404;
                }
            }
            break;

        case '/api/v1/decode':
            if ($method === 'POST') {
                $signalId = $input['signal_id'] ?? null;
                $mode = $input['mode'] ?? 'auto';
                
                if (!$signalId) {
                    $response = ['status' => 'error', 'message' => 'Signal ID required'];
                    $code = 400;
                } else {
                    $decoded = $analyzer->decodeSignal($signalId, $mode);
                    
                    $response = [
                        'status' => 'success',
                        'signal_id' => $signalId,
                        'decoded' => $decoded
                    ];
                    $code = 200;
                }
            }
            break;

        // Agent Coordination Endpoints
        case '/api/v1/share':
            if ($method === 'POST') {
                // Verify authentication for sharing
                if (!$wallet || !$auth->verify($wallet, $signature)) {
                    $response = ['status' => 'error', 'message' => 'Authentication required'];
                    $code = 401;
                } else {
                    $signalData = $input['signal'] ?? null;
                    
                    if (!$signalData) {
                        $response = ['status' => 'error', 'message' => 'Signal data required'];
                        $code = 400;
                    } else {
                        $sharedId = $network->shareSignal($wallet, $signalData);
                        
                        $response = [
                            'status' => 'success',
                            'shared_id' => $sharedId,
                            'message' => 'Signal shared with network'
                        ];
                        $code = 200;
                    }
                }
            }
            break;

        case '/api/v1/network/signals':
            if ($method === 'GET') {
                $filters = [
                    'frequency_min' => $_GET['freq_min'] ?? null,
                    'frequency_max' => $_GET['freq_max'] ?? null,
                    'modulation' => $_GET['modulation'] ?? null,
                    'classification' => $_GET['classification'] ?? null,
                    'limit' => intval($_GET['limit'] ?? 100)
                ];
                
                $signals = $network->getNetworkSignals($filters);
                
                $response = [
                    'status' => 'success',
                    'count' => count($signals),
                    'signals' => $signals
                ];
                $code = 200;
            }
            break;

        case '/api/v1/consensus':
            if ($method === 'POST') {
                if (!$wallet) {
                    $response = ['status' => 'error', 'message' => 'Wallet address required'];
                    $code = 401;
                } else {
                    $signalId = $input['signal_id'] ?? null;
                    $classification = $input['classification'] ?? null;
                    $confidence = $input['confidence'] ?? 0.5;
                    
                    if (!$signalId || !$classification) {
                        $response = ['status' => 'error', 'message' => 'Signal ID and classification required'];
                        $code = 400;
                    } else {
                        $consensus = $network->submitVote($wallet, $signalId, $classification, $confidence);
                        
                        $response = [
                            'status' => 'success',
                            'consensus' => $consensus,
                            'message' => 'Vote submitted'
                        ];
                        $code = 200;
                    }
                }
            }
            break;

        // Device Management Endpoints
        case '/api/v1/devices':
            if ($method === 'GET') {
                $devices = $analyzer->listDevices();
                
                $response = [
                    'status' => 'success',
                    'count' => count($devices),
                    'devices' => $devices
                ];
                $code = 200;
            }
            break;

        case '/api/v1/devices/' . (preg_match('/^\/api\/v1\/devices\/(.+)\/configure$/', $path, $matches) ? $matches[1] : ''):
            if ($method === 'POST' && isset($matches[1])) {
                $deviceId = $matches[1];
                $config = $input['config'] ?? [];
                
                $success = $analyzer->configureDevice($deviceId, $config);
                
                if ($success) {
                    $response = ['status' => 'success', 'message' => 'Device configured'];
                    $code = 200;
                } else {
                    $response = ['status' => 'error', 'message' => 'Configuration failed'];
                    $code = 400;
                }
            }
            break;

        case '/api/v1/devices/' . (preg_match('/^\/api\/v1\/devices\/(.+)\/status$/', $path, $matches) ? $matches[1] : ''):
            if ($method === 'GET' && isset($matches[1])) {
                $deviceId = $matches[1];
                $status = $analyzer->getDeviceStatus($deviceId);
                
                if ($status) {
                    $response = ['status' => 'success', 'device_status' => $status];
                    $code = 200;
                } else {
                    $response = ['status' => 'error', 'message' => 'Device not found'];
                    $code = 404;
                }
            }
            break;

        // Health Check
        case '/api/v1/health':
            $response = [
                'status' => 'success',
                'service' => 'NWO Signal Spectrum API',
                'version' => '1.0.0',
                'timestamp' => date('c')
            ];
            $code = 200;
            break;

        default:
            $response = ['status' => 'error', 'message' => 'Endpoint not found: ' . $path];
            $code = 404;
    }
} catch (Exception $e) {
    $response = ['status' => 'error', 'message' => $e->getMessage()];
    $code = 500;
}

http_response_code($code);
echo json_encode($response, JSON_PRETTY_PRINT);
