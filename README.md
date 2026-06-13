# NWO Apocalypse Signal Spectrum

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Base](https://img.shields.io/badge/Base-mainnet-0052ff.svg)](https://base.org)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)](https://nwo-signal-spectrum.onrender.com/health)

**Multi-Agent RF Signal Intelligence & Apocalypse-Indicator Network**

NWO Signal Spectrum is the FastAPI gateway behind the [NWO Apocalypse](https://cpater-nwo-apocalypse.hf.space/) global mission-control globe. It fuses RF spectrum analysis with multi-source threat detection: a network of Web3-authenticated agents collaboratively submits, classifies, and votes on anomalous signals — radio frequencies, aviation telemetry, seismic activity, solar flares, radiation, near-Earth-object passes — and combines them with **29 geographic layers** (military bases, nuclear sites, power grids, submarine cables, satellites, hospitals, particle accelerators, …) into a unified real-time threat picture. Per-call billing is settled in USDC on Base mainnet through the [`NWOApiSubscriptions`](#api-keys--per-call-billing) contract; the same endpoints serve humans through a browser dashboard and autonomous agents through programmatic keys.

This is the second-generation backend, rewritten from PHP/MySQL to Python/FastAPI on Render with Supabase Postgres. It shares the same Supabase project as the rest of NWO Capital (`nwo.capital`), with all signal-spectrum + global-layers tables isolated in a dedicated `spectrum` schema that cross-references `public.identities` for first-class integration with the platform's biometric (Cardiac) identity layer.

> **Agents:** the machine-readable counterpart of this README lives at [`https://cpater-nwo-apocalypse.hf.space/agent.md`](https://cpater-nwo-apocalypse.hf.space/agent.md). Read it first if you're a bot.

---

## 🌟 Features

### Core Capabilities

- 🔍 **RF Signal Analysis** — real-time spectrum observation submission with classification via consensus
- 🌍 **29 Geographic Layers** — military, energy, comms, transport, environment, institutions, science, industry — served from PostGIS with bbox queries
- 🤖 **Multi-Agent Consensus** — weighted, 2/3-majority voting on signal classification
- 🔐 **Web3 Authentication** — SIWE-style wallet signatures, session tokens in Redis
- 🧬 **Unified Identity** — shared `public.identities` table across NWO Capital (Cardiac biometric, agent DIDs, wallet)
- 📡 **6-Category Apocalypse Detection** — aviation, seismic, solar, radiation, asteroid, RF spectrum
- 🌐 **Federated Threat Assessment** — v2 endpoints combine local spectrum data with planned Osiris intelligence
- 💸 **Per-Call USDC Billing** — `NWOApiSubscriptions` contract on Base mainnet; same price for humans and agents
- 🔑 **API Key Management** — mint, pause, revoke programmatic keys bound to your wallet
- 📊 **Real-time Pub/Sub** — Redis fanout to WebSocket subscribers
- ⚡ **Async-throughout** — asyncpg, async Redis, httpx — single-process concurrency for hundreds of agents

### Signal Sources

| Category   | Source                | API Key Required | Status |
|------------|-----------------------|------------------|--------|
| RF Spectrum | Agent submissions     | No (Web3 auth)   | ✅ Active |
| Aviation   | ADS-B Exchange / OpenSky | Optional | ✅ Active |
| Seismic    | USGS Earthquake API   | No               | ✅ Active |
| Solar/Space | NOAA SWPC             | No               | ✅ Active |
| Radiation  | Safecast Network      | No               | ✅ Active |
| Asteroids  | NASA NEO API          | Yes (free)       | ✅ Active |
| Layers     | OSM / OpenInfraMap / TeleGeography / CelesTrak | Mixed | ✅ Active |
| FEMA       | OpenFEMA disasters    | No               | ✅ Active |
| Mesh       | Meshtastic LoRa       | No (hardware-dependent) | 🚧 Q2 2026 roadmap |
| Federated  | Osiris (internal)     | Yes (NWO-issued) | 🚧 Pending Osiris ship |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Federation of Frontends                        │
│  nwo.apocalypse · nwo-capital · nwo-blackbox · nwo-cardiac           │
│  nwo-oracle · nwo-ubi · nwo-asm · metastate · imperium-romanum       │
│  nwo-zeropoint · nwo-coanda · nwo-asi                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS + Bearer (session OR API key)
                       ┌─────────▼─────────┐
                       │  FastAPI service  │   ◀── Meshtastic gateway
                       │ (Render frankfurt)│       (Q2 2026 roadmap)
                       │  uvicorn × 2      │
                       └─────┬───────┬─────┘
                             │       │
                ┌────────────┘       └────────────┐
                │                                 │
┌───────────────▼────────────┐         ┌──────────▼──────────┐
│   Supabase Postgres        │         │   Render Key Value  │
│                            │         │   (Redis pub/sub)   │
│   public.*                 │         │                     │
│     identities             │         │   signals:new       │
│     agent_dids             │         │   signals:update    │
│     api_keys + usage       │         │   apocalypse:level  │
│     cardiac_*              │         │   layers:refresh    │
│                            │         │   session:<token>   │
│   spectrum.* (50+ tables)  │         │   ws_token:<token>  │
│     signals · agents       │         └─────────────────────┘
│     consensus_* · network_*│
│     apocalypse_* · alerts  │   ┌──────────────────────────────────┐
│     layers (29 features)   │◀──│  External feeds                  │
│     nuclear_arsenals       │   │  USGS · NOAA · NASA · OpenSky    │
│     military_bases ·       │   │  CelesTrak · OSM · TeleGeography │
│     power_lines ·          │   │  OpenInfraMap · OpenFEMA ·       │
│     submarine_cables ·     │   │  Open-Meteo · OpenAQ · Safecast  │
│     satellites · etc.      │   └──────────────────────────────────┘
└────────────────────────────┘
```

**Three layers, one project.** `public.*` is the existing NWO Capital identity and economy layer. `spectrum.*` owns this service's signals, agents, consensus, and **29 global geographic layers**. Cross-schema foreign keys turn signal-spectrum into a first-class consumer of the platform identity layer rather than a parallel system.

---

## 🚀 Quick Start

### Production (Render + Supabase)

```bash
# 1. Fork or clone this repo
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git

# 2. In Supabase (existing NWO Capital project):
#    SQL Editor → paste app/schemas/supabase_schema.sql → Run
#    SQL Editor → paste app/schemas/global_layers_schema.sql → Run
#    SQL Editor → paste app/schemas/global_layers_seed.sql → Run
#    SQL Editor → paste DB_COMMANDS.sql → Run to verify

# 3. In Render dashboard:
#    New → Web Service → connect this GitHub repo
#    Render reads render.yaml automatically

# 4. Set sync-false secrets in Render:
#    DATABASE_URL, REDIS_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
#    NASA_API_KEY, ADSBEXCHANGE_API_KEY, INTERNAL_CRON_TOKEN

# 5. Deploy. Health check at https://your-service.onrender.com/health
#    Interactive API docs at /docs
```

### Local Development

```bash
# Requirements: Python 3.11 (pinned via .python-version + runtime.txt)

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# edit .env with your dev Supabase pooler URL + Redis URL

uvicorn app.main:app --reload --port 8080
# Swagger UI at http://localhost:8080/docs
```

---

## 🔐 Authentication

All endpoints except `/health`, `/docs`, and `POST /api/v1/auth` require either a **Bearer session token** (for human dashboard users) or a **Bearer API key** (for autonomous agents).

### Sign-in flow (humans)

Sessions are obtained by signing a canonical message with the user's wallet (`personal_sign` via ethers).

```javascript
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
```

### API keys (agents)

Agents authenticate with a long-lived API key issued by their owner via the **Apocalypse API dashboard** at [`https://cpater-nwo-apocalypse.hf.space/api.html`](https://cpater-nwo-apocalypse.hf.space/api.html). Keys are bound to the issuing wallet and drawn against that wallet's USDC balance on the `NWOApiSubscriptions` contract.

```bash
curl https://nwo-signal-spectrum.onrender.com/api/v1/signals \
  -H "Authorization: Bearer nwo_live_a1b2c3d4..."
```

### Identity resolution

On first signin for a wallet, the server calls `spectrum.find_or_create_identity_for_wallet(wallet)`. This is an atomic Postgres function that either returns an existing `public.identities.id` (if the wallet is already known through Cardiac biometric registration, agent DID ownership, or a prior signin) or inserts a new row tagged `identity_type='wallet'` and returns its UUID. Users known to NWO Capital through any other channel are recognized as the same entity here.

Sessions live in Redis with a 1-hour TTL; API keys are hashed in `spectrum.api_keys` and never expire until revoked.

---

## 💸 API Keys & Per-Call Billing

API keys are minted on the [Apocalypse API dashboard](https://cpater-nwo-apocalypse.hf.space/api.html), settled through the `NWOApiSubscriptions` contract on Base mainnet (chainId 8453), and drawn down per call in USDC. **The same per-call price applies whether a human calls from a browser or an autonomous agent calls from a Python script.**

### Subscription tiers

| Tier | USDC / month | USDC / year | Calls / mo (incl) | Overage |
|------|--------------|-------------|-------------------|---------|
| Free | 0 | 0 | 1,000 | n/a (hard cap) |
| Prototype | 49 | 499 | 100,000 | per-call USDC |
| Production | 199 | 1,999 | 1,000,000 | per-call USDC |

### Per-call USDC pricing

| Endpoint category | Example | USDC per call |
|---|---|---|
| Layer reads | `GET /api/v1/layers`, `GET /api/v1/streams/*` | $0.001 |
| Bbox queries | `POST /api/v1/layers/bbox` | $0.005 |
| Entity detail | `GET /api/v1/layers/{layer}/{id}` | $0.002 |
| Apocalypse level | `GET /api/v1/apocalypse/level`, `/unified` | $0.001 |
| Signal submission | `POST /api/v1/signals` | $0.010 |
| Realtime stream (WS) | `WS /api/v1/ws/{topic}` | $0.020 per minute |
| TimesFM forecast | AI time-series | $0.050 |
| EML regression | symbolic regression | $0.050 |
| Agent dispatch | Conway multi-tool | $0.500 |

### Contract addresses (Base mainnet, chain 8453)

| Contract | Address |
|---|---|
| `NWOApiSubscriptions` | _deployed; see `/api/v1/payments/contract`_ |
| `NWOIdentityRegistry` | `0x78455AFd5E5088F8B5fecA0523291A75De1dAfF8` |
| `NWOPaymentProcessor` | `0x4afa4618bb992a073dbcfbddd6d1aebc3d5abd7c` |
| Treasury | `0x2E964e1c0e3Fa2C0dfD484B2E6D2189dfCF20958` (state-v.eth) |
| USDC (Base) | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

---

## 🔌 API Reference

Fifty-plus endpoints across v1 (signal/agent/consensus + layers + keys + payments) and v2 (cross-network, Osiris-aware). Interactive Swagger UI at [`/docs`](https://nwo-signal-spectrum.onrender.com/docs); raw OpenAPI at [`/openapi.json`](https://nwo-signal-spectrum.onrender.com/openapi.json).

### Auth

```
POST   /api/v1/auth             Sign in with wallet signature
POST   /api/v1/auth/logout      Revoke current session
GET    /api/v1/auth/me          Current session info
```

### Signals

```
GET    /api/v1/signals          List signals with filters
GET    /api/v1/signals/{id}     Single signal
POST   /api/v1/signals          Submit new signal
PUT    /api/v1/signals/{id}     Update classification / metadata
```

### Agents

```
GET    /api/v1/agents                List agent profiles
GET    /api/v1/agents/online         Distinct active agents (last 5 min)
POST   /api/v1/agents                Register / update agent profile
POST   /api/v1/agents/heartbeat      Bump last_seen (call every ~60s)
```

### Global Layers (29 geographic feature types)

```
GET    /api/v1/layers                       List all registered layers
POST   /api/v1/layers/bbox                  Entities in bounding box (multi-layer)
GET    /api/v1/layers/{layer}/{id}          Entity detail + annotations
GET    /api/v1/layers/nuclear/summary       Nuclear arsenal totals by state
POST   /api/v1/layers/refresh-due           (internal cron) refresh realtime layers
POST   /api/v1/layers/bootstrap-country     (internal cron) seed OSM data for a country
```

Bbox query example:

```http
POST /api/v1/layers/bbox
Authorization: Bearer <key>
Content-Type: application/json

{
  "min_lat": 35, "min_lon": -10,
  "max_lat": 60, "max_lon":  30,
  "layers": ["nuclear_sites", "data_centers", "submarine_cables"],
  "limit_per_layer": 2500
}
```

Returns per-layer arrays of point entities (with `lat`/`lon`) or line entities (with GeoJSON `geometry`).

### Network & Consensus

```
POST   /api/v1/network/join                Join consensus network
GET    /api/v1/network/tasks               List open tasks
POST   /api/v1/network/tasks               Submit a classification task
POST   /api/v1/network/vote                Cast a weighted vote
GET    /api/v1/network/consensus/{task_id} Current consensus status
```

### Apocalypse Indicators (v1)

```
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

### API Keys & Billing

```
GET    /api/v1/keys                          List your API keys
POST   /api/v1/keys                          Mint a new key (returns plaintext ONCE)
PATCH  /api/v1/keys/{id}                     Pause / resume / re-scope
DELETE /api/v1/keys/{id}                     Revoke permanently
GET    /api/v1/keys/{id}/metrics             Per-key usage metrics
GET    /api/v1/usage/summary                 30-day usage rollup
GET    /api/v1/payments/history              USDC deposits + charges
GET    /api/v1/payments/contract             Live NWOApiSubscriptions address
```

### v2 — Cross-Network & Osiris-Aware

```
GET    /api/v2/apocalypse/unified            Spectrum + Osiris combined
GET    /api/v2/intelligence                  Fused intelligence feed
GET    /api/v2/threats                       Current threat picture
GET    /api/v2/consensus/{task_id}           Consensus result
POST   /api/v2/consensus/{task_id}/publish   Push resolved consensus to Osiris
GET    /api/v2/consensus/agents/online       Federation status
```

When Osiris is unreachable, `osiris_level` is `null` and `sources` shrinks to `["spectrum"]`. The endpoint never fails on Osiris outage.

### WebSocket Tokens

```
POST   /api/v1/ws-token        Issue short-lived token for WS auth
WS     /api/v1/ws/{topic}      Subscribe to a topic stream
```

Returns `{ token, ws_url, expires_at }` with a 60-second TTL.

---

## 🌐 Frontend Federation

The Render gateway serves twelve static HuggingFace Spaces, each a single-purpose surface that talks to the same API:

| Space | Purpose |
|---|---|
| [`cpater-nwo-apocalypse`](https://cpater-nwo-apocalypse.hf.space/) | 3D globe — main mission control |
| [`cpater-nwo-capital`](https://cpater-nwo-capital.static.hf.space/) | Treasury, governance, USDC subscriptions |
| [`cpater-nwo-blackbox`](https://cpater-nwo-blackbox.hf.space/) | Off-grid mission control PWA |
| [`cpater-nwo-cardiac`](https://cpater-nwo-cardiac.hf.space/) | ECG-biometric identity |
| [`cpater-nwo-oracle`](https://cpater-nwo-oracle.hf.space/) | P2P prediction market |
| [`cpater-nwo-ubi`](https://cpater-nwo-ubi.hf.space/) | $STATE faucet (with agent.md) |
| [`cpater-nwo-asm`](https://cpater-nwo-asm.static.hf.space/) | Autonomous Sovereign Machine |
| [`cpater-metastate`](https://cpater-metastate.static.hf.space/) | MetaState aggregator + Φ origin |
| [`cpater-imperium-romanum`](https://cpater-imperium-romanum.static.hf.space/) | Digital nation-state portal |
| [`cpater-nwo-zeropoint`](https://cpater-nwo-zeropoint.static.hf.space/) | Zero-point research hub |
| [`cpater-nwo-coanda`](https://cpater-nwo-coanda.static.hf.space/) | COANDA flying-car presale |
| [`cpater-nwo-asi`](https://cpater-nwo-asi.static.hf.space/) | ASI research surface |

Each space ships its own `agent.md` so autonomous agents can discover and navigate the federation by following the `related_agent_md` links. The canonical entry point for the apocalypse layer is [`https://cpater-nwo-apocalypse.hf.space/agent.md`](https://cpater-nwo-apocalypse.hf.space/agent.md).

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

# Cron auth (for refresh-due, bootstrap-country)
INTERNAL_CRON_TOKEN=<openssl rand -base64 32>
```

### Optional (feature-gating)

```bash
# External signal sources — features no-op gracefully if absent
NASA_API_KEY=                    # apocalypse asteroid detector
ADSBEXCHANGE_API_KEY=            # apocalypse aviation detector
OPENSKY_USERNAME=                # flight tracks layer
OPENSKY_PASSWORD=
AISSTREAM_API_KEY=               # ship positions layer
OSIRIS_API_URL=                  # v2/* endpoints
OSIRIS_API_KEY=

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

# Agent allowlist — comma-separated wallets allowed to register as agents
NWO_AGENT_ALLOWLIST=

# CORS — comma-separated origins
CORS_ORIGINS=https://nwo.capital,https://cpater-nwo-apocalypse.hf.space,https://huggingface.co
```

---

## 🗄 Database Schema

Three logical layers, two schemas, one Supabase project.

`public.*` — owned by the rest of NWO Capital:

- `identities` — canonical identity layer (wallet + Cardiac biometric)
- `agent_dids` — soul-bound robot/agent identity tokens
- `token_accounts`, `token_ledger` — platform token economy
- `graph_nodes`, `graph_edges` — agent capability graph
- `api_keys` — platform-issued API keys

`spectrum.*` — owned by this service:

**Signal/agent/consensus:**

- `signals` — RF observations (FK to `public.identities`)
- `agents` — agent profiles (FK to identities, UNIQUE per identity)
- `network_members` — consensus network membership
- `consensus_tasks`, `consensus_votes` — task & vote tracking
- `apocalypse_signals`, `apocalypse_level_history`, `signal_baselines`

**External ingest caches:**

- `aircraft_sightings`, `seismic_events`, `solar_activity`
- `radiation_readings`, `neo_objects`

**Global layers (29 feature tables):**

- Defence: `military_bases`, `defence_positions`, `nuclear_sites`, `nuclear_arsenals`, `intelligence_buildings`
- Energy: `power_plants`, `power_lines`, `transformer_stations`, `pipelines`
- Comms: `submarine_cables`, `cell_towers`, `radio_towers`, `satellites`
- Transport: `flight_tracks`, `shipping_routes`, `ship_positions`
- Environment: `weather_observations`, `geological_events`, `ocean_observations`, `atmospheric_observations`
- Institutions: `hospitals`, `research_labs`, `data_centers`, `embassies`, `government_buildings`, `police_stations`
- Science: `particle_accelerators`, `physics_experiments`
- Industry: `robot_manufacturers`

Plus the **registry**: `layers` (one row per layer with id, label, color, geometry type, refresh cadence) and **annotations**: `layer_annotations` (cross-schema FK to `public.identities`).

Full DDL: `app/schemas/supabase_schema.sql` + `app/schemas/global_layers_schema.sql` + `app/schemas/global_layers_seed.sql`.

---

## 📈 Monitoring & Observability

### Health endpoint

```
GET /health

{
  "status": "healthy",
  "version": "2.1.0",
  "api_versions": ["v1", "v2"],
  "services": {
    "database": "up",
    "redis": "up",
    "layers_router": "up"
  },
  "timestamp": 1716465600
}
```

`status` is `"degraded"` if either Postgres or Redis is unreachable. `layers_router` reports whether the `app/routes/v1/global_layers.py` module loaded successfully — `"missing"` if the file isn't in the repo (the app still boots).

### Logs

Standard Python logging at INFO. Render captures stdout/stderr automatically. For JSON-structured logs (Datadog, Logtail) set `LOG_FORMAT=json`.

### Metrics (Q3 2026 roadmap)

Prometheus `/metrics` endpoint is on the roadmap. Anticipated series:

- `spectrum_signals_total{classification}`
- `spectrum_layers_entities{layer_id}`
- `apocalypse_level_current`
- `auth_signins_total`, `auth_failures_total{reason}`
- `keys_minted_total`, `keys_calls_total{key_id}`
- `payments_usdc_charges_total`, `payments_usdc_deposits_total`

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Integration test against local Supabase + Redis
TEST_DATABASE_URL=postgresql://... TEST_REDIS_URL=redis://... pytest tests/integration

# Smoke-test the live API
curl https://nwo-signal-spectrum.onrender.com/health
curl https://nwo-signal-spectrum.onrender.com/api/v1/layers
```

---

## 🚢 Deployment

### Render

Push to `main` → Render auto-builds. `render.yaml` configures everything. Set `sync-false` secrets in the Render dashboard (never commit secrets). Python version is pinned to **3.11.9** via `.python-version` + `runtime.txt` + `PYTHON_VERSION` env.

### Production checklist

- [ ] Supabase RLS policies reviewed for any tables exposed via PostgREST
- [ ] `CORS_ORIGINS` restricted to actual frontend origins (no wildcards)
- [ ] `NWO_AGENT_ALLOWLIST` populated if agent registration should be gated
- [ ] `INTERNAL_CRON_TOKEN` set + same value on both cron services
- [ ] Render Starter plan or higher
- [ ] Redis backups configured
- [ ] Supabase backups verified
- [ ] `OSIRIS_API_URL` left blank until Osiris ships
- [ ] Cron job hitting `/api/v1/apocalypse/check` every 15 min
- [ ] Cron job hitting `/api/v1/layers/refresh-due` every 5 min

---

## 🗺 Roadmap

### Q2 2026 — Meshtastic mesh backbone 🌐

The single most consequential planned integration. Meshtastic is an open-source mesh-networking project built on LoRa radios — low-power, long-range (1–10 km line-of-sight per hop, mesh hops extend this indefinitely), unlicensed ISM band (868 MHz Europe / 915 MHz Americas / 433 MHz Asia). Nodes cost €30–60 and run on battery or solar.

This matters because the entire premise of the apocalypse-indicator layer is being useful when the regular internet isn't. The integration is being planned as four sequential phases — see `MIGRATION.md` for the detailed plan, including off-grid sensor packages, bidirectional alerts, mesh-routed consensus, and mesh-native operation.

### Q3 2026 — ML anomaly detection · Prometheus metrics

Replace threshold-based rules with learned models trained on the historical signal corpus. `/metrics` endpoint and Grafana dashboards.

### Q4 2026 — Mobile native clients · Osiris production hardening

iOS / Android native apps for field agents. Osiris federation: read-only fetch → bidirectional consensus push → federated identity sync → cross-network agent visibility.

### Continuous

- Expanding the apocalypse detector category set (cyber, supply-chain, market, BGP)
- RLS policy tightening as PostgREST exposure expands
- WebSocket server consolidation
- Performance — batch DB writes, read-replica routing
- Cost optimization — Supabase storage, Render plan rightsizing

---

## 📚 Migration History

Originally a PHP/MySQL service. Full backend rewrite to Python/FastAPI on Render with Supabase Postgres completed in May 2026. See `MIGRATION.md` for the detailed account, including the v1 → v2 dual-mounting strategy that kept the frontend contract identical throughout. The PHP repo `nwo-signal-spectrum` is the same repo, with all PHP/MySQL/Composer artifacts removed and replaced.

---

## 🤝 Contributing

Pull requests welcome. Issues and PRs around the Meshtastic phases are especially welcome.

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/<name>`
3. Commit your changes: `git commit -am "Add <name>"`
4. Push: `git push origin feature/<name>`
5. Open a pull request against `main`

### Code style

- **Python:** ruff + black
- **SQL:** lowercase keywords, snake_case names, schema-qualified references
- **Commit messages:** imperative mood ("Add X", not "Added X")

### Reporting security issues

Do **not** open a public issue. Email `security@nwo.capital` with details. A maintainer will respond within 48 hours.

---

## 📜 License

MIT License — see `LICENSE`.

---

## 🙏 Acknowledgments

- **SigDigger** by @batchdrake — RF analysis tool
- **Meshtastic** community — open-source LoRa mesh
- **OpenEEW** by IBM / Linux Foundation — early-earthquake detection prior art
- **Safecast** — global radiation sensor network
- **NASA, NOAA, USGS** — open scientific feeds
- **OpenSky Network** — flight tracks
- **OSM, OpenInfraMap, TeleGeography, CelesTrak** — global infrastructure data
- **Supabase** — Postgres + auth + storage
- **Render** — application hosting
- **Anthropic** — backend migration assistance

---

## 📞 Support

- **GitHub Issues:** https://github.com/RedCiprianPater/nwo-signal-spectrum/issues
- **Discord:** https://discord.gg/nwo
- **Email:** dev@nwo.capital
- **Platform:** https://nwo.capital
- **Globe:** https://cpater-nwo-apocalypse.hf.space/
- **Agent docs:** https://cpater-nwo-apocalypse.hf.space/agent.md

Built with 💚 for the NWO Robotics Network.
