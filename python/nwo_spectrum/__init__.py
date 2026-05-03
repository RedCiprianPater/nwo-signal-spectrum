"""
NWO Signal Spectrum Python Client

Usage:
    from nwo_spectrum import SignalClient
    
    client = SignalClient(api_url="http://localhost:8080", wallet_address="0x...")
    signals = client.get_signals()
"""

import requests
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Signal:
    """Represents a detected signal"""
    id: str
    frequency_hz: int
    bandwidth_hz: int
    modulation: str
    signal_strength_dbm: float
    confidence: float
    classification: str
    timestamp: datetime
    agent: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class AnalysisResult:
    """Represents a spectrum analysis result"""
    analysis_id: str
    status: str
    signals: List[Signal]
    started_at: datetime
    completed_at: Optional[datetime] = None


class SignalClient:
    """Client for NWO Signal Spectrum API"""
    
    def __init__(self, api_url: str, wallet_address: Optional[str] = None, 
                 private_key: Optional[str] = None):
        """
        Initialize the client
        
        Args:
            api_url: Base URL of the API (e.g., http://localhost:8080)
            wallet_address: Ethereum wallet address for authentication
            private_key: Private key for signing requests (optional)
        """
        self.api_url = api_url.rstrip('/')
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.session = requests.Session()
        
        if wallet_address:
            self.session.headers.update({
                'X-NWO-Wallet': wallet_address
            })
    
    def _sign_request(self, data: dict) -> str:
        """Sign request with private key"""
        if not self.private_key:
            return ""
        
        # In production, use eth-account to sign
        # For now, return mock signature
        return "0x" + "a" * 130
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated request"""
        url = f"{self.api_url}{endpoint}"
        
        # Add signature header for POST requests
        if method == 'POST' and self.wallet_address:
            signature = self._sign_request(kwargs.get('json', {}))
            self.session.headers['X-NWO-Signature'] = signature
        
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def analyze_spectrum(self, frequency: float, bandwidth: float = 2e6, 
                        duration: int = 10, device: str = 'default') -> str:
        """
        Start spectrum analysis
        
        Args:
            frequency: Center frequency in Hz
            bandwidth: Bandwidth in Hz
            duration: Analysis duration in seconds
            device: SDR device ID
            
        Returns:
            Analysis ID
        """
        result = self._request('POST', '/api/v1/analyze', json={
            'frequency': frequency,
            'bandwidth': bandwidth,
            'duration': duration,
            'device': device
        })
        
        return result['analysis_id']
    
    def get_signals(self, freq_min: Optional[float] = None,
                   freq_max: Optional[float] = None,
                   modulation: Optional[str] = None,
                   limit: int = 50) -> List[Signal]:
        """
        Get detected signals
        
        Args:
            freq_min: Minimum frequency filter
            freq_max: Maximum frequency filter
            modulation: Modulation type filter
            limit: Maximum number of results
            
        Returns:
            List of Signal objects
        """
        params = {'limit': limit}
        if freq_min:
            params['freq_min'] = freq_min
        if freq_max:
            params['freq_max'] = freq_max
        if modulation:
            params['modulation'] = modulation
        
        result = self._request('GET', '/api/v1/signals', params=params)
        
        signals = []
        for sig_data in result.get('signals', []):
            signals.append(Signal(
                id=sig_data['id'],
                frequency_hz=sig_data['frequency_hz'],
                bandwidth_hz=sig_data.get('bandwidth_hz', 0),
                modulation=sig_data.get('modulation', 'unknown'),
                signal_strength_dbm=sig_data.get('signal_strength_dbm', -100),
                confidence=sig_data.get('confidence', 0),
                classification=sig_data.get('classification', 'unknown'),
                timestamp=datetime.fromisoformat(sig_data['timestamp'].replace('Z', '+00:00')),
                agent=sig_data.get('agent'),
                metadata=sig_data.get('metadata')
            ))
        
        return signals
    
    def decode_signal(self, signal_id: str, mode: str = 'auto') -> dict:
        """
        Decode a specific signal
        
        Args:
            signal_id: Signal ID to decode
            mode: Decoding mode (auto, FM, AM, SSB, etc.)
            
        Returns:
            Decoded signal data
        """
        return self._request('POST', '/api/v1/decode', json={
            'signal_id': signal_id,
            'mode': mode
        })
    
    def share_signal(self, signal: dict) -> str:
        """
        Share signal with the network
        
        Args:
            signal: Signal data to share
            
        Returns:
            Shared signal ID
        """
        result = self._request('POST', '/api/v1/share', json={
            'signal': signal
        })
        
        return result['shared_id']
    
    def get_network_signals(self, **filters) -> List[dict]:
        """
        Get signals from entire agent network
        
        Returns:
            List of signals with consensus data
        """
        result = self._request('GET', '/api/v1/network/signals', params=filters)
        return result.get('signals', [])
    
    def submit_classification(self, signal_id: str, classification: str, 
                             confidence: float = 0.8) -> dict:
        """
        Submit classification vote for consensus
        
        Args:
            signal_id: Signal to classify
            classification: Proposed classification
            confidence: Confidence level (0-1)
            
        Returns:
            Consensus result
        """
        return self._request('POST', '/api/v1/consensus', json={
            'signal_id': signal_id,
            'classification': classification,
            'confidence': confidence
        })
    
    def list_devices(self) -> List[dict]:
        """List available SDR devices"""
        result = self._request('GET', '/api/v1/devices')
        return result.get('devices', [])
    
    def health_check(self) -> dict:
        """Check API health"""
        return self._request('GET', '/api/v1/health')


class SignalMonitor:
    """Real-time signal monitor with callbacks"""
    
    def __init__(self, client: SignalClient):
        self.client = client
        self.callbacks = []
        self.running = False
    
    def on_signal(self, callback):
        """Register callback for new signals"""
        self.callbacks.append(callback)
    
    def start(self, frequency: float, bandwidth: float = 2e6):
        """Start monitoring"""
        import threading
        
        self.running = True
        
        def monitor():
            analysis_id = self.client.analyze_spectrum(frequency, bandwidth)
            
            while self.running:
                signals = self.client.get_signals(
                    freq_min=frequency - bandwidth/2,
                    freq_max=frequency + bandwidth/2,
                    limit=10
                )
                
                for signal in signals:
                    for callback in self.callbacks:
                        callback(signal)
                
                import time
                time.sleep(1)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


# Example usage
if __name__ == '__main__':
    # Create client
    client = SignalClient(
        api_url="http://localhost:8080",
        wallet_address="0x..."
    )
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health}")
    
    # List devices
    devices = client.list_devices()
    print(f"Available devices: {devices}")
    
    # Start analysis
    analysis_id = client.analyze_spectrum(
        frequency=433.92e6,  # 433.92 MHz
        bandwidth=2e6,
        duration=30
    )
    print(f"Started analysis: {analysis_id}")
    
    # Get signals
    signals = client.get_signals(limit=5)
    for sig in signals:
        print(f"Signal {sig.id}: {sig.modulation} at {sig.frequency_hz} Hz")
