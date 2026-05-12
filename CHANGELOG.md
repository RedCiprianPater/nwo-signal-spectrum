# NWO Signal Spectrum Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-05-12

### Added
- **Apocalypse Indicators** - 6-category threat detection system
  - Aviation anomaly detection (ADS-B Exchange)
  - Seismic monitoring (USGS Earthquake API)
  - Solar activity tracking (NOAA SWPC)
  - Radiation monitoring (Safecast Network)
  - Asteroid close approach alerts (NASA NEO)
  - Pandemic surveillance (WHO/Global Health Observatory)
- **Apocalypse Level System** - 1-5 scale with automated calculations
- **New API Endpoints**
  - `GET /api/v1/apocalypse/level` - Current threat level
  - `GET /api/v1/apocalypse/alerts` - Active alerts
  - `GET /api/v1/apocalypse/check` - Run all checks
  - `GET /api/v1/apocalypse/aviation` - Aviation anomalies
  - `GET /api/v1/apocalypse/seismic` - Seismic activity
  - `GET /api/v1/apocalypse/solar` - Solar flares/storms
  - `GET /api/v1/apocalypse/radiation` - Radiation spikes
  - `GET /api/v1/apocalypse/asteroid` - NEO tracking
- **Database Schema Updates**
  - `apocalypse_signals` table
  - `apocalypse_level_history` table
  - `aircraft_sightings` table
  - `seismic_events` table
  - `solar_activity` table
  - `radiation_readings` table
  - `neo_objects` table
- **Cron Job** - Automated apocalypse checking every 15 minutes
- **Telegram Notifications** - Critical alert notifications
- **WebSocket Support** - Real-time apocalypse level updates

### Changed
- **API Router** - Complete rewrite with new endpoint structure
- **Documentation** - Comprehensive README with all new features
- **Docker Compose** - Added apocalypse checker service
- **Health Check** - Now includes apocalypse level metrics

### Fixed
- Database connection pooling issues
- Redis pub/sub reliability
- Agent consensus timeout handling

## [1.1.0] - 2026-04-15

### Added
- Agent network consensus voting
- Web3 wallet authentication
- Real-time WebSocket feeds
- Signal sharing between agents
- Frequency band management

### Changed
- Improved SigDigger integration
- Enhanced signal classification ML
- Better error handling

## [1.0.0] - 2026-03-20

### Added
- Initial release
- RF signal analysis with SigDigger
- Multi-agent coordination
- Web3 authentication
- Basic REST API
- Docker deployment
- Prometheus metrics

---

## Migration Guide: 1.x to 2.0

### Database
```bash
# Run migration scripts
php scripts/migrate.php
php scripts/migrate-apocalypse.php
```

### API Changes
- Old: `/api/v1/spectrum/signals`
- New: `/api/v1/signals` (same functionality)

### New Environment Variables
```env
NASA_API_KEY=your_nasa_api_key
ADSBEXCHANGE_API_KEY=your_adsb_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Cron Jobs
Add to crontab:
```bash
*/15 * * * * /usr/bin/php /path/to/scripts/apocalypse-check.php
```
