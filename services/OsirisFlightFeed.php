<?php
/**
 * Osiris Flight Feed Service
 * Fetches and processes flight tracking data from Osiris
 */

namespace NWOSignalSpectrum\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class OsirisFlightFeed
{
    private Client $httpClient;
    private string $baseUrl;
    private array $cache;
    
    public function __construct(string $baseUrl = 'http://localhost:3000')
    {
        $this->baseUrl = $baseUrl;
        $this->httpClient = new Client([
            'timeout' => 10,
            'connect_timeout' => 5
        ]);
        $this->cache = [];
    }
    
    /**
     * Fetch current flights from Osiris
     */
    public function getFlights(array $filters = []): array
    {
        $cacheKey = 'flights_' . md5(json_encode($filters));
        
        // Return cached data if fresh (< 30 seconds)
        if (isset($this->cache[$cacheKey]) && 
            (time() - $this->cache[$cacheKey]['time']) < 30) {
            return $this->cache[$cacheKey]['data'];
        }
        
        try {
            $response = $this->httpClient->get("{$this->baseUrl}/api/flights", [
                'query' => $filters
            ]);
            
            $data = json_decode($response->getBody()->getContents(), true);
            
            $this->cache[$cacheKey] = [
                'data' => $data,
                'time' => time()
            ];
            
            return $data;
            
        } catch (GuzzleException $e) {
            error_log("Osiris flight feed error: " . $e->getMessage());
            return $this->cache[$cacheKey]['data'] ?? [];
        }
    }
    
    /**
     * Detect aviation anomalies
     */
    public function detectAnomalies(string $region = 'global'): array
    {
        $flights = $this->getFlights(['region' => $region]);
        
        $anomalies = [];
        $baseline = $this->getBaselineTraffic($region);
        $current = count($flights['flights'] ?? []);
        
        // Detect traffic spikes
        if ($current > $baseline * 1.5) {
            $anomalies[] = [
                'type' => 'traffic_spike',
                'severity' => $current > $baseline * 2.0 ? 'high' : 'medium',
                'region' => $region,
                'current_count' => $current,
                'baseline' => $baseline,
                'multiplier' => round($current / $baseline, 2),
                'timestamp' => date('c')
            ];
        }
        
        // Detect military aircraft concentration
        $military = array_filter($flights['flights'] ?? [], function($f) {
            return ($f['military'] ?? false) || 
                   in_array($f['type'] ?? '', ['MIL', 'C130', 'F16', 'F35']);
        });
        
        if (count($military) > 5) {
            $anomalies[] = [
                'type' => 'military_concentration',
                'severity' => count($military) > 10 ? 'high' : 'medium',
                'region' => $region,
                'military_count' => count($military),
                'timestamp' => date('c')
            ];
        }
        
        // Detect private jet clusters (Davos-style events)
        $privateJets = array_filter($flights['flights'] ?? [], function($f) {
            $types = ['GLF', 'G650', 'F900', 'CL60', 'GLEX', 'FA7X'];
            return in_array($f['type'] ?? '', $types);
        });
        
        if (count($privateJets) > 20) {
            $anomalies[] = [
                'type' => 'elite_gathering',
                'severity' => 'medium',
                'region' => $region,
                'private_jet_count' => count($privateJets),
                'timestamp' => date('c')
            ];
        }
        
        return $anomalies;
    }
    
    /**
     * Get baseline traffic for a region
     */
    private function getBaselineTraffic(string $region): int
    {
        // Historical averages stored in database
        $baselines = [
            'global' => 8000,
            'europe' => 2500,
            'north_america' => 3000,
            'asia' => 2000,
            'davos' => 150
        ];
        
        return $baselines[$region] ?? 1000;
    }
    
    /**
     * Get flight by callsign
     */
    public function getFlight(string $callsign): ?array
    {
        $flights = $this->getFlights();
        
        foreach ($flights['flights'] ?? [] as $flight) {
            if (($flight['callsign'] ?? '') === $callsign) {
                return $flight;
            }
        }
        
        return null;
    }
}
