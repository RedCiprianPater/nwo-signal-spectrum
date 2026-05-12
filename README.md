# NWO Apocalypse Signal Spectrum

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PHP](https://img.shields.io/badge/PHP-8.0+-blue.svg)](https://php.net/)
[![Web3](https://img.shields.io/badge/Web3-Ethereum-3C3C3D)](https://ethereum.org/)

**Multi-Agent RF Signal Analysis & Apocalypse Detection Network**

NWO Signal Spectrum is a distributed signal intelligence platform that combines RF spectrum analysis with apocalyptic threat detection. It enables agents to collaboratively identify, classify, and respond to anomalous signals—from radio frequencies to seismic activity, solar flares, and asteroid approaches.

## 🌟 Features

### Core Capabilities
- **🔍 RF Signal Analysis** - Real-time spectrum monitoring with SigDigger integration
- **🤖 Multi-Agent Consensus** - Distributed classification via agent voting
- **🔐 Web3 Authentication** - Wallet-based access control
- **📊 Real-time Dashboard** - Live signal feeds and analytics
- **🚨 Apocalypse Indicators** - 6-category threat detection system

### Signal Types Supported
| Category | Source | Status |
|----------|--------|--------|
| RF Spectrum | SigDigger/RTL-SDR | ✅ Active |
| Aviation | ADS-B Exchange | ✅ Active |
| Seismic | USGS Earthquake API | ✅ Active |
| Solar/Space | NOAA SWPC | ✅ Active |
| Radiation | Safecast Network | ✅ Active |
| Asteroids | NASA NEO API | ✅ Active |

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git
cd nwo-signal-spectrum

# Start services
docker-compose up -d

# Access dashboard
open http://localhost:8080
```

### Manual Installation

```bash
# Requirements: PHP 8.0+, MySQL 5.7+, Redis, Python 3.8+

# 1. Install PHP dependencies
composer install

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure database
cp config/database.example.php config/database.php
# Edit config/database.php with your credentials

# 4. Run migrations
php scripts/migrate.php

# 5. Start services
php -S localhost:8080 -t public/
redis-server
python3 scripts/spectrum-monitor.py
```

## 📡 Signal Sources

### RF Spectrum (SigDigger)
```php
use NWOSignalSpectrum\SignalAnalyzer;

$analyzer = new SignalAnalyzer($device);
$signals = $analyzer->scan(
    frequency: 433920000, // 433.92 MHz
    bandwidth: 2000000,   // 2 MHz
    duration: 30          // 30 seconds
);
```

### Aviation Anomalies (ADS-B)
```php
use NWOSignalSpectrum\ApocalypseIndicators;

$indicators = new ApocalypseIndicators($db);
$anomaly = $indicators->detectAviationAnomaly('davos');

// Returns: 450 business jets (3.0x normal)
```

### Seismic Monitoring (USGS)
```php
$seismic = $indicators->detectSeismicAnomaly(hours: 24);

// Returns: Cluster of 4 M6+ earthquakes
```

### Solar Activity (NOAA)
```php
$solar = $indicators->detectSolarAnomaly();

// Returns: X-class flare detected
```

## 🔌 API Reference

### Authentication
All API requests require Web3 wallet authentication:

```http
POST /api/v1/auth
Content-Type: application/json
X-NWO-Wallet: 0x...
X-NWO-Signature: 0x...

{
  "message": "Authenticate for NWO Signal Spectrum",
  "timestamp": 1715500800
}
```

### Signal Endpoints

#### Submit Signal
```http
POST /api/v1/signals
Authorization: Bearer <token>

{
  "frequency_hz": 433920000,
  "bandwidth_hz": 12500,
  "modulation": "FM",
  "signal_strength_dbm": -75,
  "classification": "unknown",
  "location": {
    "lat": 40.7128,
    "lon": -74.0060
  }
}
```

#### Get Signals
```http
GET /api/v1/signals?freq_min=433000000&freq_max=434000000&limit=50
```

#### Submit Consensus Vote
```http
POST /api/v1/signals/{id}/vote
Authorization: Bearer <token>

{
  "classification": "voice",
  "confidence": 0.85,
  "notes": "Likely aviation communication"
}
```

### Apocalypse Endpoints

#### Get Current Level
```http
GET /api/v1/apocalypse/level
```

Response:
```json
{
  "level": 3,
  "description": "High - Multiple concerning signals",
  "active_signals": 5,
  "breakdown": {
    "aviation": 2,
    "seismic": 1,
    "solar": 1,
    "radiation": 1
  },
  "timestamp": "2026-05-12T12:00:00Z"
}
```

#### Get Active Alerts
```http
GET /api/v1/apocalypse/alerts?severity=critical&hours=24
```

## 🤖 Agent Network

### Join Network
```php
use NWOSignalSpectrum\AgentNetwork;

$network = new AgentNetwork($client);
$network->join([
    'wallet' => '0x...',
    'capabilities' => ['rf_analysis', 'signal_classification'],
    'region' => 'europe'
]);
```

### Submit Task for Consensus
```php
$task = [
    'type' => 'signal_classification',
    'signal_id' => 'sig_12345',
    'proposed_class' => 'military_drone',
    'evidence' => ['spectrogram_hash', 'audio_sample']
];

$consensus = $network->submitTask($task);
// Returns consensus after agent voting
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Web UI  │  │  Mobile  │  │  Python  │  │   CLI    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │  (PHP/Router)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│ SignalAnalyzer │  │ AgentNetwork    │  │ Apocalypse     │
│ (RF/SDR)       │  │ (Consensus)     │  │ Indicators     │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Database      │
                    │  (MySQL/Redis)  │
                    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables
```env
# Database
DB_HOST=localhost
DB_NAME=nwo_spectrum
DB_USER=spectrum
DB_PASS=secure_password

# Redis (for real-time)
REDIS_HOST=localhost
REDIS_PORT=6379

# Web3
ETHEREUM_RPC=https://mainnet.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x...

# APIs
NASA_API_KEY=your_nasa_api_key
ADSBEXCHANGE_API_KEY=your_adsb_key

# Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Signal Processing Settings
```php
// config/spectrum.php
return [
    'scan_interval' => 60,        // seconds
    'anomaly_threshold' => 3.0,   // sigma
    'consensus_threshold' => 0.67, // 2/3 majority
    'agent_timeout' => 300,       // seconds
    
    'apocalypse' => [
        'check_interval' => 900,  // 15 minutes
        'alert_channels' => ['telegram', 'discord', 'webhook'],
        'min_severity' => 'medium'
    ]
];
```

## 📈 Monitoring

### Prometheus Metrics
```
spectrum_signals_total{type="rf"}
spectrum_signals_anomaly{type="aviation"}
spectrum_agents_online
spectrum_consensus_votes_total
apocalypse_level_current
apocalypse_alerts_total{severity="critical"}
```

### Health Check
```http
GET /health

{
  "status": "healthy",
  "version": "1.2.0",
  "services": {
    "database": "up",
    "redis": "up",
    "sigdigger": "up"
  },
  "agents_online": 47
}
```

## 🧪 Testing

```bash
# Run PHPUnit tests
./vendor/bin/phpunit

# Run Python tests
pytest tests/

# Integration tests
php scripts/test-integration.php

# Load testing
wrk -t12 -c400 -d30s http://localhost:8080/api/v1/signals
```

## 🚀 Deployment

### Production Checklist
- [ ] Configure SSL/TLS
- [ ] Set up Redis cluster
- [ ] Enable MySQL replication
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Enable Prometheus monitoring
- [ ] Configure backups

### Kubernetes
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nwo-spectrum
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nwo-spectrum
  template:
    spec:
      containers:
      - name: api
        image: nwo/spectrum:latest
        ports:
        - containerPort: 8080
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

### Coding Standards
- PHP: PSR-12
- Python: PEP 8
- JavaScript: ESLint Airbnb

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Acknowledgments

- SigDigger by @batchdrake
- OpenEEW by IBM/Linux Foundation
- Safecast global sensor network
- NASA Open APIs
- NOAA Space Weather Prediction Center
- Kyle McDonald's AEWS (inspiration)

## 📞 Support

- GitHub Issues: https://github.com/RedCiprianPater/nwo-signal-spectrum/issues
- Discord: https://discord.gg/nwo
- Email: dev@nwo.capital

---

**Built with 💚 for the NWO Robotics Network**
