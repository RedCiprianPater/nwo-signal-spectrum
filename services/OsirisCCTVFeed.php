<?php
/**
 * Osiris CCTV Feed Service
 * Fetches CCTV camera data from Osiris
 */

namespace NWOSignalSpectrum\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class OsirisCCTVFeed
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
     * Get active cameras from Osiris
     */
    public function getActiveCameras(string $region = 'global'): array
    {
        $cacheKey = 'cctv_' . $region;
        
        if (isset($this->cache[$cacheKey]) && 
            (time() - $this->cache[$cacheKey]['time']) < 60) {
            return $this->cache[$cacheKey]['data'];
        }
        
        try {
            $response = $this->httpClient->get("{$this->baseUrl}/api/cctv", [
                'query' => ['region' => $region]
            ]);
            
            $data = json_decode($response->getBody()->getContents(), true);
            
            $this->cache[$cacheKey] = [
                'data' => $data['cameras'] ?? [],
                'time' => time()
            ];
            
            return $data['cameras'] ?? [];
            
        } catch (GuzzleException $e) {
            error_log("Osiris CCTV feed error: " . $e->getMessage());
            return $this->cache[$cacheKey]['data'] ?? [];
        }
    }
}
