<?php
/**
 * Cross-Platform Agent Consensus API
 * Enables agents from both Osiris and Spectrum to vote on threats
 */

require_once __DIR__ . '/../../../vendor/autoload.php';

use NWOSignalSpectrum\AgentNetwork\ConsensusEngine;
use NWOSignalSpectrum\Auth\Web3Auth;

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');

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
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$pathParts = explode('/', trim($path, '/'));
$action = end($pathParts);

try {
    $consensus = new ConsensusEngine();
    
    switch ($action) {
        case 'consensus':
            if ($method === 'POST') {
                // POST /api/v2/agents/consensus - Start new consensus
                $data = json_decode(file_get_contents('php://input'), true);
                
                if (!$data || !isset($data['type'])) {
                    http_response_code(400);
                    echo json_encode(['error' => 'Missing required fields']);
                    exit;
                }
                
                $consensusId = $consensus->startConsensus([
                    'type' => $data['type'],
                    'data' => $data['data'] ?? [],
                    'timeout' => $data['timeout'] ?? 300,
                    'min_votes' => $data['min_votes'] ?? 5,
                    'created_by' => $auth->getWalletAddress()
                ]);
                
                echo json_encode([
                    'success' => true,
                    'consensus_id' => $consensusId,
                    'status' => 'voting',
                    'timeout' => $data['timeout'] ?? 300
                ]);
                
            } elseif ($method === 'GET') {
                // GET /api/v2/agents/consensus - List active consensus
                $active = $consensus->getActiveConsensus();
                
                echo json_encode([
                    'timestamp' => date('c'),
                    'active_consensus' => $active,
                    'count' => count($active)
                ]);
            }
            break;
            
        case 'vote':
            // POST /api/v2/agents/consensus/vote
            if ($method !== 'POST') {
                http_response_code(405);
                echo json_encode(['error' => 'Method not allowed']);
                exit;
            }
            
            $data = json_decode(file_get_contents('php://input'), true);
            
            if (!$data || !isset($data['consensus_id']) || !isset($data['vote'])) {
                http_response_code(400);
                echo json_encode(['error' => 'Missing consensus_id or vote']);
                exit;
            }
            
            $result = $consensus->submitVote([
                'consensus_id' => $data['consensus_id'],
                'agent_wallet' => $auth->getWalletAddress(),
                'vote' => $data['vote'],
                'confidence' => $data['confidence'] ?? 0.5,
                'evidence' => $data['evidence'] ?? []
            ]);
            
            echo json_encode([
                'success' => true,
                'vote_recorded' => true,
                'consensus_status' => $result['status'],
                'current_votes' => $result['votes'],
                'confidence' => $result['confidence']
            ]);
            break;
            
        case 'active':
            // GET /api/v2/agents/consensus/active
            $active = $consensus->getActiveConsensus();
            $mostRecent = $active[0] ?? null;
            
            echo json_encode([
                'timestamp' => date('c'),
                'consensus' => $mostRecent
            ]);
            break;
            
        case 'status':
            // GET /api/v2/agents/status
            $status = $consensus->getAgentStatus([
                'wallet' => $auth->getWalletAddress()
            ]);
            
            echo json_encode([
                'timestamp' => date('c'),
                'agents' => $status['agents'] ?? [],
                'online' => $status['online'] ?? 0,
                'voting' => $status['voting'] ?? 0,
                'total' => $status['total'] ?? 0
            ]);
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
