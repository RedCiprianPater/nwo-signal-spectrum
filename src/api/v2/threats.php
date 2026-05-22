<?php
/**
 * Unified Threats API
 * Aggregates threats from both Osiris and Spectrum
 */

require_once __DIR__ . '/../../../vendor/autoload.php';

use NWOSignalSpectrum\Services\UnifiedIntelligence;
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

try {
    $intelligence = new UnifiedIntelligence();
    
    if ($method === 'GET') {
        // GET /api/v2/threats/unified
        $filters = [
            'hours' => intval($_GET['hours'] ?? 24),
            'min_severity' => $_GET['min_severity'] ?? 'low',
            'category' => $_GET['category'] ?? null,
            'region' => $_GET['region'] ?? null,
            'lat' => $_GET['lat'] ?? null,
            'lng' => $_GET['lng'] ?? null,
            'radius_km' => $_GET['radius'] ?? 100
        ];
        
        $threats = $intelligence->getUnifiedThreats($filters);
        
        // Calculate unified threat score
        $threatScore = calculateUnifiedThreatScore($threats);
        
        echo json_encode([
            'timestamp' => date('c'),
            'filters' => $filters,
            'threat_score' => $threatScore,
            'threat_level' => getThreatLevel($threatScore),
            'threats' => $threats,
            'summary' => [
                'total' => count($threats),
                'by_category' => aggregateByCategory($threats),
                'by_severity' => aggregateBySeverity($threats)
            ]
        ]);
        
    } elseif ($method === 'POST') {
        // POST /api/v2/threats/unified - Report new threat
        $data = json_decode(file_get_contents('php://input'), true);
        
        if (!$data) {
            http_response_code(400);
            echo json_encode(['error' => 'Invalid JSON']);
            exit;
        }
        
        $threatId = $intelligence->reportThreat([
            'source' => $data['source'] ?? 'manual',
            'category' => $data['category'],
            'severity' => $data['severity'],
            'title' => $data['title'],
            'description' => $data['description'],
            'location' => $data['location'] ?? null,
            'metadata' => $data['metadata'] ?? [],
            'reported_by' => $auth->getWalletAddress()
        ]);
        
        echo json_encode([
            'success' => true,
            'threat_id' => $threatId,
            'timestamp' => date('c')
        ]);
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Internal server error',
        'message' => $e->getMessage()
    ]);
}

function calculateUnifiedThreatScore(array $threats): float {
    $score = 0;
    $weights = [
        'critical' => 10,
        'high' => 5,
        'medium' => 2,
        'low' => 0.5
    ];
    
    foreach ($threats as $threat) {
        $severity = strtolower($threat['severity'] ?? 'low');
        $score += $weights[$severity] ?? 0.5;
    }
    
    // Normalize to 0-100 scale
    return min(100, $score);
}

function getThreatLevel(float $score): string {
    if ($score >= 80) return 'CRITICAL';
    if ($score >= 60) return 'HIGH';
    if ($score >= 40) return 'MODERATE';
    if ($score >= 20) return 'ELEVATED';
    return 'LOW';
}

function aggregateByCategory(array $threats): array {
    $categories = [];
    foreach ($threats as $threat) {
        $cat = $threat['category'] ?? 'unknown';
        $categories[$cat] = ($categories[$cat] ?? 0) + 1;
    }
    return $categories;
}

function aggregateBySeverity(array $threats): array {
    $severities = [];
    foreach ($threats as $threat) {
        $sev = $threat['severity'] ?? 'low';
        $severities[$sev] = ($severities[$sev] ?? 0) + 1;
    }
    return $severities;
}
