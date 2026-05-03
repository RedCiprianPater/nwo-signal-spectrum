# NWO Signal Spectrum

[![NWO Robotics](https://img.shields.io/badge/NWO-Robotics-00ff88)](https://nwo.capital)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![API Version](https://img.shields.io/badge/API-v1.0.0-orange)](openapi.yaml)

**Signal Analysis & Spectrum Intelligence for NWO Robotics**

NWO Signal Spectrum integrates [SigDigger](https://github.com/batchdrake/sigdigger)'s core DSP capabilities (via suscan/sigutils) into the NWO Robotics ecosystem, enabling AI agents to analyze radio signals, share spectrum intelligence, and coordinate signal analysis operations across the agent network.

## 🌐 Overview

NWO Signal Spectrum provides a bridge between software-defined radio (SDR) hardware and the NWO Robotics agent network. It allows robots and AI agents to:

- **Analyze RF signals** in real-time across multiple frequency bands
- **Detect and classify** modulation types (FSK, PSK, ASK, analog voice/video)
- **Decode signals** using extensible codec interfaces
- **Monitor spectrum** for anomalies, interference, and threats
- **Share intelligence** across the agent network via P2P protocol
- **Coordinate analysis** through consensus-based classification

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NWO Robotics Ecosystem                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Signal     │  │   Signal     │  │   Signal     │              │
│  │  Analyzer    │  │   Decoder    │  │   Monitor    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼─────────────────┼─────────────────┼──────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │   NWO Signal Spectrum API  │
              │  ┌─────────────────────┐  │
              │  │   Spectrum Engine   │  │
              │  │  (suscan/sigutils)  │  │
              │  └─────────────────────┘  │
              └───────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │   SDR     │    │  Signal   │    │  Agent    │
    │  Device   │    │   Share   │    │  Network  │
    │(SoapySDR) │    │  Protocol │    │ (P2P/API) │
    └───────────┘    └───────────┘    └───────────┘
```

## 🚀 Features

### Signal Analysis
- **Real-time spectrum analysis** with configurable FFT size and refresh rates
- **Modulation detection**: FSK, PSK, ASK, FM, AM, SSB, analog video
- **Signal parameter estimation**: frequency, bandwidth, SNR, constellation
- **Burst signal analysis** for intermittent transmissions
- **Frequency hopping detection** and tracking

### Signal Decoding
- **Analog voice demodulation**: AM, FM, SSB
- **Digital mode decoding**: Custom codec interface for proprietary protocols
- **Video signal decoding**: Analog TV, drone FPV
- **Extensible codec system** for adding new modulation types

### Multi-Agent Coordination
- **Signal intelligence sharing** via standardized protocol
- **Distributed spectrum monitoring** across multiple agents
- **Agent-to-agent communication** via WebSocket and webhooks
- **Consensus-based classification** with reputation scoring

### Web3 Integration
- **Wallet-based API authentication** (MetaMask, WalletConnect)
- **Signal analysis NFTs** for provenance and ownership
- **On-chain signal intelligence registry** (Base Mainnet)
- **Tokenized spectrum access** for premium features

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [NWO Robotics Integration](#nwo-robotics-integration)
- [Signal Sharing Protocol](#signal-sharing-protocol)
- [Python Client](#python-client)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

- PHP 8.1+ with SQLite3 extension
- SDR hardware (RTL-SDR, HackRF, Airspy) with SoapySDR drivers
- FFTW3, libsndfile, libxml2 development libraries
- Redis (optional, for real-time updates)

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    php8.1 php8.1-sqlite3 php8.1-curl \
    libfftw3-dev libsndfile1-dev libsoapysdr-dev libxml2-dev \
    cmake build-essential git sqlite3 redis-server

# Clone with submodules
git clone --recursive https://github.com/RedCiprianPater/nwo-signal-spectrum.git
cd nwo-signal-spectrum

# Build DSP libraries
mkdir -p build && cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig

# Install PHP dependencies
composer install

# Set permissions
sudo chown -R www-data:www-data data/
sudo chmod 755 data/
```

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git
cd nwo-signal-spectrum

# Start services
docker-compose up -d

# API available at http://localhost:8080
```

## ⚡ Quick Start

### 1. Start the API Server

```bash
# Using PHP built-in server
php -S localhost:8080 -t api/

# Or using Apache/Nginx with the provided .htaccess
```

### 2. Connect from NWO Agent

```python
from nwo_spectrum import SignalClient

# Initialize client with wallet
client = SignalClient(
    api_url="http://localhost:8080",
    wallet_address="0xYourWalletAddress"
)

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# List available SDR devices
devices = client.list_devices()
for device in devices:
    print(f"{device['name']} ({device['driver']}): {'Available' if device['available'] else 'In Use'}")

# Start spectrum analysis
analysis_id = client.analyze_spectrum(
    frequency=433.92e6,  # 433.92 MHz (ISM band)
    bandwidth=2e6,       # 2 MHz bandwidth
    duration=30,         # 30 seconds
    device='rtlsdr-0'
)
print(f"Started analysis: {analysis_id}")

# Get detected signals
signals = client.get_signals(limit=10)
for sig in signals:
    print(f"[{sig.modulation}] {sig.frequency_hz/1e6:.3f} MHz "
          f"({sig.signal_strength_dbm:.1f} dBm, {sig.confidence*100:.0f}% confidence)")
```

### 3. Share Signal with Network

```python
# Detected a suspicious signal
suspicious_signal = {
    'signal_id': 'sig-001',
    'frequency_hz': 433920000,
    'bandwidth_hz': 12500,
    'modulation': 'FM',
    'signal_strength_dbm': -45,
    'confidence': 0.95,
    'classification': 'voice',
    'metadata': {
        'location': {'lat': 59.9139, 'lon': 10.7522},
        'device': 'rtl-sdr-v3',
        'antenna': 'dipole-433'
    }
}

# Share with agent network
shared_id = client.share_signal(suspicious_signal)
print(f"Shared signal: {shared_id}")

# Get network consensus
consensus = client.submit_classification(
    signal_id='sig-001',
    classification='potential_threat',
    confidence=0.87
)
print(f"Network consensus: {consensus['consensus']['classification']}")
```

## 🔌 API Endpoints

### Signal Analysis

#### Start Analysis
```http
POST /api/v1/analyze
Content-Type: application/json
X-NWO-Wallet: 0x...

{
  "frequency": 433920000,
  "bandwidth": 2000000,
  "duration": 10,
  "device": "rtlsdr-0"
}
```

**Response:**
```json
{
  "status": "success",
  "analysis_id": "a1b2c3d4e5f6...",
  "frequency": 433920000,
  "bandwidth": 2000000,
  "estimated_duration": 10
}
```

#### Get Signals
```http
GET /api/v1/signals?freq_min=433000000&freq_max=434000000&limit=50
```

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "signals": [
    {
      "id": "sig-001",
      "timestamp": "2026-05-03T10:00:00Z",
      "agent": "0xAgentWallet...",
      "frequency_hz": 433920000,
      "bandwidth_hz": 12500,
      "modulation": "FM",
      "signal_strength_dbm": -45.2,
      "confidence": 0.95,
      "classification": "voice",
      "metadata": {...}
    }
  ]
}
```

#### Decode Signal
```http
POST /api/v1/decode
Content-Type: application/json

{
  "signal_id": "sig-001",
  "mode": "FM"
}
```

### Agent Coordination

#### Share Signal
```http
POST /api/v1/share
Content-Type: application/json
X-NWO-Wallet: 0x...
X-NWO-Signature: 0x...

{
  "signal": {
    "signal_id": "sig-001",
    "frequency_hz": 433920000,
    "modulation": "FM",
    ...
  }
}
```

#### Get Network Signals
```http
GET /api/v1/network/signals?classification=voice&limit=100
```

#### Submit Consensus Vote
```http
POST /api/v1/consensus
Content-Type: application/json
X-NWO-Wallet: 0x...

{
  "signal_id": "sig-001",
  "classification": "voice",
  "confidence": 0.95
}
```

### Device Management

#### List Devices
```http
GET /api/v1/devices
```

#### Configure Device
```http
POST /api/v1/devices/rtlsdr-0/configure
Content-Type: application/json

{
  "config": {
    "sample_rate": 2048000,
    "gain": 40,
    "ppm_error": 0
  }
}
```

## 🤖 NWO Robotics Integration

### Agent Capabilities

Add to your agent's capability manifest:

```yaml
capabilities:
  signal_analysis:
    - spectrum_monitoring
    - modulation_detection
    - signal_decoding
    - burst_analysis
    - frequency_hopping_tracking
  
  coordination:
    - signal_sharing
    - distributed_analysis
    - consensus_voting
    - threat_detection
  
  web3:
    - wallet_auth
    - nft_minting
    - onchain_registry
    - tokenized_access
```

### Example: Autonomous Signal Investigation

```python
import asyncio
from nwo_spectrum import SignalClient, SignalMonitor

class SignalInvestigationAgent:
    def __init__(self, client: SignalClient):
        self.client = client
        self.threats_detected = []
    
    async def investigate_frequency(self, frequency: float):
        """Autonomous signal investigation workflow"""
        
        # 1. Analyze spectrum
        print(f"🔍 Analyzing {frequency/1e6} MHz...")
        analysis_id = await self.client.analyze_spectrum(
            frequency=frequency,
            bandwidth=5e6,
            duration=60
        )
        
        # 2. Wait for completion and get signals
        await asyncio.sleep(60)
        signals = await self.client.get_signals(
            freq_min=frequency - 2.5e6,
            freq_max=frequency + 2.5e6
        )
        
        for signal in signals:
            # 3. Decode if possible
            if signal.modulation in ['FM', 'AM']:
                decoded = await self.client.decode_signal(
                    signal.id, 
                    mode=signal.modulation
                )
                
                # 4. Analyze content for threats
                threat_level = self.analyze_content(decoded)
                
                if threat_level > 0.7:
                    # 5. Share with network
                    signal_data = {
                        'signal_id': signal.id,
                        'frequency_hz': signal.frequency_hz,
                        'modulation': signal.modulation,
                        'classification': 'threat',
                        'threat_level': threat_level,
                        'decoded_preview': decoded.get('preview', '')
                    }
                    
                    shared_id = await self.client.share_signal(signal_data)
                    print(f"🚨 Threat shared: {shared_id}")
                    
                    # 6. Get network consensus
                    consensus = await self.client.submit_classification(
                        signal_id=signal.id,
                        classification='confirmed_threat',
                        confidence=threat_level
                    )
                    
                    if consensus['consensus']['confidence'] > 0.8:
                        await self.trigger_security_alert(signal)
    
    def analyze_content(self, decoded: dict) -> float:
        """Analyze decoded content for threats"""
        # Implement threat detection logic
        # Return threat level 0-1
        return 0.5
    
    async def trigger_security_alert(self, signal):
        """Trigger security response"""
        print(f"🚨 SECURITY ALERT: Threat confirmed at {signal.frequency_hz} Hz")
        # Integrate with NWO security system

# Usage
async def main():
    client = SignalClient(
        api_url="https://nwo.capital/api/spectrum",
        wallet_address="0x..."
    )
    
    agent = SignalInvestigationAgent(client)
    await agent.investigate_frequency(433.92e6)

asyncio.run(main())
```

### Real-time Monitoring

```python
from nwo_spectrum import SignalClient, SignalMonitor

client = SignalClient(api_url="http://localhost:8080")
monitor = SignalMonitor(client)

@monitor.on_signal
def on_new_signal(signal):
    """Callback for new signals"""
    if signal.classification == 'unknown':
        # Auto-analyze unknown signals
        decoded = client.decode_signal(signal.id)
        print(f"🔍 Unknown signal decoded: {decoded}")

# Start monitoring 433 MHz ISM band
monitor.start(frequency=433.92e6, bandwidth=2e6)

# Run indefinitely
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
```

## 📡 Signal Sharing Protocol

Agents share signal intelligence using a standardized JSON format:

```json
{
  "signal_id": "uuid-v4",
  "timestamp": "2026-05-03T10:00:00Z",
  "agent_id": "0xAgentWalletAddress",
  "frequency_hz": 433920000,
  "bandwidth_hz": 12500,
  "modulation": "FM",
  "signal_strength_dbm": -45.2,
  "confidence": 0.95,
  "classification": "voice",
  "metadata": {
    "location": {
      "lat": 59.9139,
      "lon": 10.7522,
      "accuracy_m": 10
    },
    "device": "rtl-sdr-v3",
    "antenna": "dipole-433",
    "environment": "urban"
  },
  "signature": "0x...",
  "hash": "sha256:..."
}
```

### Consensus Algorithm

Network consensus is achieved through weighted voting:

```python
consensus = {
    "classification": "voice",
    "confidence": 0.89,
    "total_votes": 12,
    "breakdown": [
        {"classification": "voice", "count": 10, "avg_confidence": 0.92},
        {"classification": "data", "count": 2, "avg_confidence": 0.65}
    ],
    "participating_agents": ["0x...", "0x..."]
}
```

## 🐍 Python Client

### Installation

```bash
pip install nwo-signal-spectrum
```

### Basic Usage

```python
from nwo_spectrum import SignalClient, Signal

# Initialize
client = SignalClient(
    api_url="https://nwo.capital/api/spectrum",
    wallet_address="0x...",
    private_key="0x..."  # Optional, for signing
)

# Health check
health = client.health_check()

# Analyze spectrum
analysis_id = client.analyze_spectrum(
    frequency=433.92e6,
    bandwidth=2e6,
    duration=30
)

# Get signals
signals: list[Signal] = client.get_signals(limit=50)

# Share with network
client.share_signal({
    'frequency_hz': 433920000,
    'modulation': 'FM',
    'classification': 'voice'
})
```

## 🐳 Docker Deployment

### Quick Start

```bash
# Clone repo
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git
cd nwo-signal-spectrum

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f nwo-spectrum
```

### Environment Variables

```bash
# API Configuration
NWO_SPECTRUM_PORT=8080
NWO_SPECTRUM_DB_PATH=/data/signals.db

# Web3 Configuration
NWO_WEB3_RPC=https://mainnet.base.org
NWO_CONTRACT_ADDRESS=0x...

# SDR Configuration
SUSCAN_PATH=/usr/local/bin/suscan
DEFAULT_SDR_DEVICE=rtlsdr-0

# Redis (optional)
REDIS_URL=redis://redis:6379
```

## ⚙️ Configuration

### Signal Processing Settings

Create `config/spectrum.json`:

```json
{
  "spectrum": {
    "fft_size": 4096,
    "refresh_rate": 30,
    "averaging": 4,
    "window": "hann"
  },
  "detection": {
    "threshold_db": -60,
    "min_bandwidth_hz": 10000,
    "max_signals": 50,
    "burst_detection": true
  },
  "demodulation": {
    "enabled_modes": ["FM", "AM", "SSB", "FSK", "PSK"],
    "default_mode": "FM",
    "audio_sample_rate": 48000
  },
  "network": {
    "share_enabled": true,
    "consensus_threshold": 0.7,
    "reputation_weight": true
  }
}
```

### Device Configuration

Create `config/devices/rtlsdr-0.json`:

```json
{
  "sample_rate": 2048000,
  "center_frequency": 433920000,
  "gain": 40,
  "ppm_error": 0,
  "antenna": "dipole-433",
  "bias_tee": false
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repo
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git
cd nwo-signal-spectrum

# Install PHP dependencies
composer install

# Install Python dependencies
pip install -e ./python

# Run tests
composer test
pytest python/tests/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- Built on [SigDigger](https://github.com/batchdrake/sigdigger), [suscan](https://github.com/batchdrake/suscan), and [sigutils](https://github.com/batchdrake/sigutils) by [BatchDrake](https://github.com/batchdrake)
- NWO Robotics integration by [NWO Capital](https://nwo.capital)

## 📞 Support

- Documentation: https://docs.nwo.capital/signal-spectrum
- Issues: https://github.com/RedCiprianPater/nwo-signal-spectrum/issues
- Discord: https://discord.gg/nwo
- Twitter: [@NWOCapital](https://twitter.com/NWOCapital)

---

**Built with 💚 for the NWO Robotics Network**
