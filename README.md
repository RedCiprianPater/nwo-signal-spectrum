# NWO Apocalypse Signal Spectrum

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.115+-009688.svg)
![Web3](https://img.shields.io/badge/auth-Web3-orange.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Multi-Agent RF Signal Intelligence & Apocalypse-Indicator Network**

NWO Signal Spectrum is a distributed signal-intelligence platform that combines RF spectrum analysis with multi-source threat detection. A network of Web3-authenticated agents collaboratively submits, classifies, and votes on anomalous signals — from radio frequencies and aviation telemetry to seismic activity, solar flares, radiation anomalies, and near-Earth-object approaches. The platform fuses all of this into a unified real-time threat level, and is being architected to remain functional in degraded-connectivity scenarios via a planned Meshtastic mesh backbone.

This is the second-generation backend, rewritten from PHP/MySQL to Python/FastAPI on Render with Supabase Postgres. It shares the same Supabase project as the rest of NWO Capital (`nwo.capital/asi`), with all signal-spectrum tables isolated in a dedicated `spectrum` schema that cross-references `public.identities` for first-class integration with the platform's biometric (Cardiac) identity layer.

---

## 🌟 Features

### Core Capabilities

- 🔍 **RF Signal Analysis** — real-time spectrum observation submission with classification via consensus
- 🤖 **Multi-Agent Consensus** — weighted, 2/3-majority voting on signal classification
- 🔐 **Web3 Authentication** — SIWE-style wallet signatures, session tokens in Redis
- 🧬 **Unified Identity** — shared `public.identities` table across NWO Capital (Cardiac biometric, agent DIDs, wallet)
- 📡 **6-Category Apocalypse Detection** — aviation, seismic, solar, radiation, asteroid, RF spectrum
- 🌐 **Federated Threat Assessment** — v2 endpoints combine local spectrum data with planned Osiris intelligence
- 📊 **Real-time Pub/Sub** — Redis fanout to WebSocket subscribers on new signals, classification updates, threat-level changes
- ⚡ **Async-throughout** — asyncpg, async Redis, httpx — single-process concurrency for hundreds of agents

### Signal Sources

| Category    | Source                | API Key Required          | Status        |
|-------------|-----------------------|---------------------------|---------------|
| RF Spectrum | Agent submissions     | No (Web3 auth)            | ✅ Active      |
| Aviation    | ADS-B Exchange        | Yes ($10/mo RapidAPI)     | ✅ Active      |
| Seismic     | USGS Earthquake API   | No                        | ✅ Active      |
| Solar/Space | NOAA SWPC             | No                        | ✅ Active      |
| Radiation   | Safecast Network      | No                        | ✅ Active      |
| Asteroids   | NASA NEO API          | Yes (free, instant)       | ✅ Active      |
| Mesh        | Meshtastic LoRa       | No (hardware-dependent)   | 🚧 Q2 2026 roadmap |
| Federated   | Osiris (internal)     | Yes (NWO-issued)          | 🚧 Pending Osiris ship |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            Clients                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  React SPA  │  │   Mobile    │  │ Python SDK  │  │ Meshtastic │ │
│  │ ethers.js   │  │  (planned)  │  │  (planned)  │  │ (Q2 2026)  │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└─────────┼────────────────┼────────────────┼────────────────┼────────┘
          └────────────────┴────────────────┘                │
                           │                                 │
                  HTTPS + Bearer token                  LoRa mesh
                           │                                 │
                ┌──────────▼─────────┐         ┌────────────▼──────────┐
                │  FastAPI service   │◀────────│  Meshtastic gateway   │
                │  (Render frankfurt)│   HTTP  │  (Phase 1 ingestion)  │
                │  uvicorn × 2       │         └───────────────────────┘
                └─────┬────────┬─────┘
                      │        │
       ┌──────────────┘        └──────────────┐
       │                                       │
┌──────▼──────────┐                  ┌─────────▼─────────┐
│ Supabase Postgres│                 │ Render Key Value  │
│                  │                 │ (Redis pub/sub)   │
│  public.*        │                 │                   │
│   identities     │                 │ signals:new       │
│   agent_dids     │                 │ signals:update    │
│   token_accounts │                 │ apocalypse:level  │
│   cardiac_*      │                 │ consensus:tasks   │
│   graph_nodes    │                 │ consensus:vote    │
│                  │                 │ agents:online     │
│  spectrum.*      │                 │ session:<token>   │
│   signals        │                 │ ws_token:<token>  │
│   agents         │                 └───────────────────┘
│   consensus_*    │
│   apocalypse_*   │      ┌──────────────────────────────────┐
│   aircraft_…     │◀─────│ External feeds                   │
│   seismic_events │ cron │ NASA NEO, NOAA SWPC, USGS,       │
│   ...            │ pull │ ADS-B Exchange, Safecast, Osiris │
└──────────────────┘      └──────────────────────────────────┘
```

Two Postgres schemas, one project. `public` is the existing NWO Capital identity and economy layer. `spectrum` is everything this service owns. Cross-schema foreign keys turn signal-spectrum into a first-class consumer of the platform identity layer rather than a parallel system.

---

## 🚀 Quick Start

### Production (Render + Supabase)

The service deploys via Render's blueprint mechanism. `render.yaml` in the repo root configures everything; `.env.example` documents every environment variable.

```bash
# 1. Fork or clone this repo
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git

# 2. In Supabase (existing NWO Capital project):
#    SQL Editor → paste app/schemas/supabase_schema.sql → Run
#    Then paste DB_COMMANDS.sql → Run to verify

# 3. In Render dashboard:
#    New → Web Service → connect this GitHub repo
#    Render reads render.yaml automatically

# 4. Set sync-false secrets in Render:
#    DATABASE_URL, REDIS_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
#    NASA_API_KEY, ADSBEXCHANGE_API_KEY

# 5. Deploy. Health check at https://your-service.onrender.com/health
#    Interactive API docs at /docs
```

Full step-by-step including how to obtain each API key, where to find the Supabase pooler URL, and the post-deploy smoke test is in `MIGRATION.md`.

### Local Development

```bash
# Requirements: Python 3.12 (pinned via .python-version)

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# edit .env with your dev Supabase pooler URL + Redis URL

uvicorn app.main:app --reload --port 8080

# Visit http://localhost:8080/docs for Swagger UI
```

---

## 🔐 Authentication

All endpoints except `/health`, `/docs`, and `POST /api/v1/auth` require a Bearer session token. Sessions are obtained by signing a canonical message with the user's wallet (`personal_sign` via `ethers.signMessage` on the frontend).

### Sign-in flow

```javascript
// Frontend (React + ethers v6)
import { BrowserProvider } from "ethers";

const provider = new BrowserProvider(window.ethereum);
const signer = await provider.getSigner();
const wallet = await signer.getAddress();

const timestamp = Math.floor(Date.now() / 1000);
const nonce = crypto.randomUUID();
const message =
  `Authenticate for NWO Signal Spectrum\n` +
  `Domain: nwo.capital\n` +
  `Nonce: ${nonce}\n` +
  `Timestamp: ${timestamp}`;

const signature = await signer.signMessage(message);

const resp = await fetch("https://nwo-signal-spectrum.onrender.com/api/v1/auth", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-NWO-Wallet": wallet,
    "X-NWO-Signature": signature
  },
  body: JSON.stringify({ message, timestamp, nonce })
});

const { wallet: addr, identity_id, token, expires_at } = await resp.json();
sessionStorage.setItem("nwo_token", token);
sessionStorage.setItem("nwo_identity_id", identity_id);
```

### Identity resolution

On first signin for a wallet, the server calls `spectrum.find_or_create_identity_for_wallet(wallet)`. This is an atomic Postgres function that either returns an existing `public.identities.id` (if the wallet is already known — e.g. through Cardiac biometric registration, agent DID ownership, or a prior signal-spectrum signin) or inserts a new row tagged `identity_type='wallet'` and returns its UUID. Users known to NWO Capital through any other channel are recognized as the same entity here.

Sessions live in Redis with a 1-hour TTL, carrying both wallet and identity_id. Authenticated requests use `Authorization: Bearer <token>`.

---

## 🔌 API Reference

Thirty-six endpoints across v1 (signal/agent/consensus primitives) and v2 (cross-network, Osiris-aware). Interactive Swagger UI lives at `/docs`; raw OpenAPI at `/openapi.json`.

### Auth

```http
POST   /api/v1/auth             Sign in with wallet signature
POST   /api/v1/auth/logout      Revoke current session
GET    /api/v1/auth/me          Current session info
```

### Signals

```http
GET    /api/v1/signals          List signals with filters
GET    /api/v1/signals/{id}     Single signal
POST   /api/v1/signals          Submit new signal
PUT    /api/v1/signals/{id}     Update classification / metadata
```

**Submit signal example:**

```http
POST /api/v1/signals
Authorization: Bearer <token>
Content-Type: application/json

{
  "frequency_hz": 433920000,
  "bandwidth_hz": 12500,
  "modulation": "FM",
  "signal_strength_dbm": -75,
  "classification": "unknown",
  "location": { "lat": 40.7128, "lon": -74.0060 },
  "metadata": { "device": "rtl-sdr-v3", "antenna": "discone" }
}
```

Response includes the inserted record plus its `submitter_identity_id`, and the signal is broadcast on the `signals:new` Redis channel for WebSocket subscribers.

### Agents

```http
GET    /api/v1/agents                List online agents (filterable)
POST   /api/v1/agents                Register / update agent profile
POST   /api/v1/agents/heartbeat      Bump last_seen (call every ~60s)
```

Agent registration is keyed on identity, not wallet — one agent profile per identity. Capabilities is an array of strings (e.g. `["rf_analysis", "signal_classification", "mesh_relay"]`).

### Network & Consensus

```http
POST   /api/v1/network/join                Join consensus network
GET    /api/v1/network/tasks               List open tasks
POST   /api/v1/network/tasks               Submit a classification task
POST   /api/v1/network/vote                Cast a weighted vote
GET    /api/v1/network/consensus/{task_id} Current consensus status
```

**Submit vote example:**

```http
POST /api/v1/network/vote
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_id": 1234,
  "classification": "military_drone_telemetry",
  "confidence": 0.87,
  "notes": "Hopping pattern matches DJI OcuSync 2.0"
}
```

Response includes the vote acknowledgment plus the re-evaluated consensus result. When weighted votes for any single classification cross the 2/3 threshold, the task auto-resolves and is published on the `consensus:vote` channel.

### Apocalypse Indicators (v1)

```http
GET    /api/v1/apocalypse              Dashboard summary
GET    /api/v1/apocalypse/level        Current threat level 1–5
GET    /api/v1/apocalypse/alerts       Recent alerts (filterable)
POST   /api/v1/apocalypse/check        Run all detectors (cron)
GET    /api/v1/apocalypse/history      Level history
GET    /api/v1/apocalypse/aviation     Aviation anomaly snapshot
GET    /api/v1/apocalypse/seismic      Seismic cluster snapshot
GET    /api/v1/apocalypse/solar        Solar activity snapshot
GET    /api/v1/apocalypse/radiation    Radiation anomaly snapshot
GET    /api/v1/apocalypse/asteroid     Hazardous NEO snapshot
```

**Get current level:**

```http
GET /api/v1/apocalypse/level
Authorization: Bearer <token>

{
  "level": 3,
  "description": "High — multiple concerning signals",
  "active_signals": 5,
  "breakdown": {
    "aviation": 2,
    "seismic": 1,
    "solar": 1,
    "radiation": 1
  },
  "timestamp": "2026-05-23T12:00:00Z"
}
```

### v2 — Cross-Network & Osiris-Aware

```http
GET    /api/v2/apocalypse/unified            Spectrum + Osiris combined
GET    /api/v2/intelligence                  Fused intelligence feed
GET    /api/v2/threats                       Current threat picture
GET    /api/v2/consensus/{task_id}           Consensus result
POST   /api/v2/consensus/{task_id}/publish   Push resolved consensus to Osiris
GET    /api/v2/consensus/agents/online       Federation status
```

**Unified threat assessment:**

```http
GET /api/v2/apocalypse/unified
Authorization: Bearer <token>

{
  "unified_level": 4,
  "osiris_level": 4,
  "spectrum_level": 3,
  "sources": ["spectrum", "osiris"],
  "breakdown": {
    "spectrum": { "aviation": 2, "seismic": 1, "solar": 1, "radiation": 1 },
    "osiris": { "level": 4, "feeds": 12, "regions": ["EU", "NA"] }
  },
  "timestamp": "2026-05-23T12:00:00Z"
}
```

When Osiris is unreachable, `osiris_level` is `null` and `sources` shrinks to `["spectrum"]`. The endpoint never fails on Osiris outage.

### WebSocket Tokens

```http
POST   /api/v1/ws-token        Issue short-lived token for WS auth
```

Returns `{ token, ws_url, expires_at }` with a 60-second TTL. The WebSocket server (separate process) validates incoming tokens against the same Redis store.

---

## ⚙️ Configuration

All configuration is environment-variable-driven via `pydantic-settings`. The full set is documented in `.env.example`.

### Required

```bash
# Supabase — use the Transaction pooler URL (port 6543)
DATABASE_URL=postgresql://postgres.PROJECT:PWD@aws-0-REGION.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# Redis
REDIS_URL=rediss://default:PWD@HOST:PORT

# Web3 auth
NWO_AUTH_DOMAIN=nwo.capital
```

### Optional (feature-gating)

```bash
# External signal sources — features no-op gracefully if absent
NASA_API_KEY=                    # apocalypse asteroid detector
ADSBEXCHANGE_API_KEY=            # apocalypse aviation detector
OSIRIS_API_URL=                  # v2/* endpoints; degrade to spectrum-only if missing
OSIRIS_API_KEY=

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

# Agent allowlist — comma-separated wallets allowed to register as agents
# (leave empty to allow any verified wallet)
NWO_AGENT_ALLOWLIST=

# CORS — comma-separated origins
CORS_ORIGINS=https://nwo.capital,http://localhost:5173
```

### Application tuning

```python
# Implicit defaults — override via env vars or app/config.py
SESSION_TTL_SECONDS         = 3600     # auth session lifetime
NWO_AUTH_TIMESTAMP_WINDOW   = 300      # signed timestamp acceptance window
CONSENSUS_THRESHOLD         = 0.67     # 2/3 weighted majority
ONLINE_WINDOW_SECONDS       = 300      # agent "online" window
WS_TOKEN_TTL_SECONDS        = 60       # WebSocket auth token lifetime
```

---

## 🗄 Database Schema

Two schemas live in the same Supabase project.

**`public.*`** — owned by the rest of NWO Capital:

- `identities` — canonical identity layer (wallet + Cardiac biometric)
- `agent_dids` — soul-bound robot/agent identity tokens
- `token_accounts`, `token_ledger` — platform token economy
- `graph_nodes`, `graph_edges` — agent capability graph (4-layer hierarchy)
- `api_keys` — platform-issued API keys

**`spectrum.*`** — owned by this service:

- `signals` — RF observations (FK to `public.identities` via `submitter_identity_id`)
- `agents` — agent profiles (FK to identities, UNIQUE per identity)
- `network_members` — consensus network membership
- `consensus_tasks`, `consensus_votes` — task & vote tracking (FK to identities)
- `apocalypse_signals` — current alerts across all 6 detector categories
- `apocalypse_level_history` — rolling level snapshots
- `signal_baselines` — per-region baselines for anomaly detection
- `aircraft_sightings` — ADS-B Exchange ingest cache
- `seismic_events` — USGS ingest cache
- `solar_activity` — NOAA SWPC ingest cache
- `radiation_readings` — Safecast ingest cache
- `neo_objects` — NASA NEO ingest cache
- `signal_shares` — short-token sharing for individual signals
- `apocalypse_dashboard` (view) — dashboard summary aggregate

The schema also installs a Postgres function `spectrum.find_or_create_identity_for_wallet(text) RETURNS uuid` used by the auth flow.

Full DDL in `app/schemas/supabase_schema.sql`. Verification queries in `DB_COMMANDS.sql`.

---

## 📈 Monitoring & Observability

### Health endpoint

```http
GET /health

{
  "status": "healthy",
  "version": "2.0.0",
  "api_versions": ["v1", "v2"],
  "services": {
    "database": "up",
    "redis": "up"
  },
  "timestamp": 1716465600
}
```

`status` is `"degraded"` if either Postgres or Redis is unreachable. Render uses this as its `healthCheckPath`.

### Logs

Standard Python `logging` at INFO level by default. Render captures stdout/stderr automatically and exposes them in the dashboard's Logs tab. For JSON-structured logs (Datadog, Logtail, etc.) set `LOG_FORMAT=json` and the `python-json-logger` formatter takes over.

### Metrics (planned Q3 2026)

Prometheus metrics endpoint at `/metrics` is on the roadmap. Anticipated series:

```
spectrum_signals_total{classification}
spectrum_signals_anomaly{type}
spectrum_agents_online
spectrum_consensus_votes_total{task_type}
apocalypse_level_current
apocalypse_alerts_total{severity}
auth_signins_total
auth_failures_total{reason}
osiris_requests_total{outcome}
```

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Integration test against a local Supabase + Redis
TEST_DATABASE_URL=postgresql://... TEST_REDIS_URL=redis://... pytest tests/integration

# Load test the live API (be polite)
wrk -t4 -c50 -d30s -H "Authorization: Bearer <token>" \
    https://nwo-signal-spectrum.onrender.com/api/v1/apocalypse/level
```

---

## 🚢 Deployment

### Render (recommended)

Push to `main` → Render auto-builds. `render.yaml` configures everything. Set sync-false secrets in the Render dashboard (never commit secrets). Python version is pinned to 3.12 via `.python-version` + `PYTHON_VERSION` env.

### Production checklist

- [ ] Supabase RLS policies reviewed for any tables exposed via PostgREST
- [ ] `CORS_ORIGINS` restricted to actual frontend origins (no wildcards)
- [ ] `NWO_AGENT_ALLOWLIST` populated if agent registration should be gated
- [ ] Render Starter plan or higher (Free tier sleeps after 15 min idle)
- [ ] Redis backups configured (Render Key Value or Upstash dashboard)
- [ ] Supabase backups verified (Project Settings → Database → Backups)
- [ ] `OSIRIS_API_URL` left blank until Osiris service is in production
- [ ] Cron job hitting `/api/v1/apocalypse/check` every 15 min (external scheduler)

### Migration from PHP

See `MIGRATION.md` for the full PHP-to-Python migration narrative. The HTTP contract is unchanged so the React frontend on `nwo.capital/asi` keeps working through the cutover.

---

## 🗺 Roadmap

### Q2 2026 — Meshtastic mesh backbone 🌐

The single most consequential planned integration. Meshtastic is an open-source mesh-networking project built on LoRa radios — low-power, long-range (1–10 km line-of-sight per hop, mesh hops extend this indefinitely), unlicensed ISM band (868 MHz Europe / 915 MHz Americas / 433 MHz Asia). Nodes cost €30–60 and run on battery or solar.

This matters because the entire premise of the apocalypse-indicator layer is *being useful when the regular internet isn't*. A unified threat assessment that goes dark the moment cellular networks degrade is worth less than nothing. Meshtastic gives the platform a fallback transport genuinely independent of carrier infrastructure.

The integration is being planned as four sequential phases.

**Phase 1 — Ingestion (Q2 early).** A new service `app/services/meshtastic.py` connects to a Meshtastic gateway node via the official `meshtastic` Python package, supporting USB serial, BLE, and TCP/MQTT transports. Two new tables under the `spectrum` schema: `mesh_nodes` (node_id, public_key, last_seen, last_position, hardware_model) and `mesh_messages` (sender_node_id, channel, timestamp, payload, signal_strength_dbm, rssi, snr). A background task pulls messages off the gateway and writes them in. Off-grid sensor packages — Geiger counters with mesh nodes, seismic sensors on Meshtastic-equipped Raspberry Pis, remote SDR feeders — can report observations into the spectrum platform without internet connectivity at the sensor location. A single gateway node with a wired uplink ingests for the whole mesh.

**Phase 2 — Bidirectional alerts (Q2 mid).** A Redis subscriber service watches the `apocalypse:level` channel. When the unified threat level transitions to 4 or 5, the service formats a short broadcast (Meshtastic's payload limit is ~230 bytes) and publishes it to a private encrypted channel (`nwo-alerts`, AES-256, pre-shared key distributed out of band). Every mesh node on that channel receives the alert within seconds — without internet, without subscribing to anything centralized. A new endpoint `POST /api/v1/mesh/broadcast` lets authenticated agents send manual alerts subject to severity-based rate limits and identity-based authorization (only identities with the `mesh_broadcast` capability can send). This is the first feature that makes the platform genuinely useful in a degraded scenario rather than just nicer-to-have.

**Phase 3 — Mesh-routed consensus (Q2 late).** The consensus voting protocol is extended so that votes can be cast as Meshtastic messages signed by the voter's wallet. The mesh node carries a key derived from the agent's identity (registered on Phase 1 join). When a gateway receives a signed mesh vote, it verifies the signature against `public.identities.primary_wallet`, then inserts into `spectrum.consensus_votes`. Identities can now participate in consensus when their internet is degraded — vital for distributed agents in field conditions where carrier connectivity is unreliable. Eventually a mesh-only sub-consensus can resolve locally and sync back to the central DB when uplink returns.

**Phase 4 — Mesh-native operation (Q3+).** Standalone Meshtastic devices preloaded with NWO firmware. Edge inference on-device for simple anomaly detection — radiation deviation from baseline, sudden RSSI shifts on monitored frequencies — without needing a Raspberry Pi alongside. Store-and-forward of alerts when no gateway is reachable. A reference hardware kit (Heltec or Lilygo board + Geiger tube + GPS + solar + battery) so participating agents can self-provision a sensor node for under €100. The endgame is a self-organizing physical-layer network that augments the centralized API for as long as both exist, and can survive on its own when the centralized API can't.

Hardware procurement and firmware development happen in a sibling repo `nwo-meshtastic-firmware` (not yet public). Software issues are tracked in this repo tagged `meshtastic`.

### Q3 2026 — Machine Learning Anomaly Detection 🧠

Replace the threshold-based rules in `apocalypse_indicators.py` with learned models. Train on the historical signal corpus accumulated through Q1–Q2 — by then there will be enough labeled data from consensus-classified signals to train classifiers per category. Edge-deployable variants for Phase 4 Meshtastic devices. Models versioned in Supabase Storage; rollback via env-var version pin.

### Q3 2026 — Prometheus Metrics & Grafana 📊

`/metrics` endpoint exposing the metrics series listed under Monitoring. Grafana dashboards mirroring the existing `grafana/` configs. Alerting rules for level transitions, Osiris federation drops, abnormal agent counts.

### Q4 2026 — Mobile Native Clients 📱

iOS and Android native apps (Swift / Kotlin, not React Native) for field agents. WalletConnect for signing. Background submission of sensor data. Push notifications for level-4+ alerts. Tight integration with phone GPS, microphone (audio spectrum), and camera (object tagging for ground-truth correlation with aerial sightings).

### Q4 2026 — Osiris Production Hardening 🛡

The v2 endpoints are wired and ready for Osiris. When the Osiris service ships, the integration progresses through: read-only intelligence fetch → bidirectional consensus push → federated identity sync → cross-network agent visibility. Each step is gated by an env-var feature flag.

### Continuous

- Expanding the apocalypse detector category set (cyber indicators, supply-chain signals, market dislocations, BGP routing anomalies)
- RLS policy tightening as PostgREST exposure expands
- WebSocket server consolidation (currently the FastAPI service issues tokens but the WS endpoint runs separately)
- Performance — batch DB writes for high-cadence agent submissions; read-replica routing once query volume justifies it
- Cost optimization — Supabase storage usage, Render plan rightsizing

---

## 📚 Migration History

The platform was originally a PHP service backed by MySQL on the `nwo.capital/webapp/api` shared host. Full backend rewrite to Python/FastAPI on Render with Supabase Postgres was completed in May 2026 — see `MIGRATION.md` for the detailed account, including the v1 → v2 dual-mounting strategy that kept the frontend contract identical throughout. The PHP repo `nwo-signal-spectrum` is the same repo, with all PHP/MySQL/Composer artifacts removed and replaced.

Key migration choices documented separately:

- Why FastAPI over Flask, Django, or Node — see `MIGRATION.md`
- Why Supabase shared schema over a separate project — see `PATCH_NOTES.md`
- Why Render over Cloudflare Workers — see this README's stack section above
- Why asyncpg + Supavisor transaction pooler over `supabase-py` PostgREST — see `app/db.py` docstring

---

## 🤝 Contributing

Pull requests welcome. Issues and PRs around the Meshtastic phases are especially welcome — both software and reference-hardware contributions.

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/<name>`
3. Commit your changes: `git commit -am "Add <name>"`
4. Push: `git push origin feature/<name>`
5. Open a pull request against `main`

### Code style

- Python: ruff + black (config in `pyproject.toml` — TBD)
- SQL: lowercase keywords, snake_case names, schema-qualified references
- Commit messages: imperative mood ("Add X", not "Added X")

### Reporting security issues

Do not open a public issue. Email `security@nwo.capital` with details. A maintainer will respond within 48 hours.

---

## 📜 License

MIT License — see `LICENSE`.

---

## 🙏 Acknowledgments

- **SigDigger** by [@batchdrake](https://github.com/BatchDrake) — RF analysis tool that informs spectrum monitoring
- **Meshtastic** community — open-source LoRa mesh that the Q2 2026 roadmap depends on
- **OpenEEW** by IBM / Linux Foundation — early-earthquake detection prior art
- **Safecast** — global radiation sensor network with open data
- **NASA Open APIs** — NEO feed, planetary data
- **NOAA SWPC** — space weather prediction
- **USGS** — earthquake feeds
- **Supabase** — Postgres + auth + storage platform
- **Render** — application hosting
- **Anthropic** — backend migration assistance
- Kyle McDonald's AEWS — long-standing inspiration for civilian threat-monitoring infrastructure

---

## 📞 Support

- **GitHub Issues**: <https://github.com/RedCiprianPater/nwo-signal-spectrum/issues>
- **Discord**: <https://discord.gg/nwo>
- **Email**: <dev@nwo.capital>
- **Platform**: <https://nwo.capital/asi>

Built with 💚 for the NWO Robotics Network.
