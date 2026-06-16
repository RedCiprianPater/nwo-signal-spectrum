# NWO Apocalypse Signal Spectrum

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688.svg)](https://fastapi.tiangolo.com/)
[![Base mainnet](https://img.shields.io/badge/Base-8453-0052ff.svg)](https://basescan.org)
[![Status: open per-call](https://img.shields.io/badge/access-open%20per--call-13ffa0)](https://nwo.capital)
[![Version 2.1.0](https://img.shields.io/badge/version-2.1.0-ffd64a.svg)](https://github.com/RedCiprianPater/nwo-signal-spectrum/releases)

> Global mission control for planetary signals. A 3D globe of 33 geographic layers
> plus 12 live event streams, a seven-detector unified apocalypse aggregator, the
> NWO RSS community radar with driven-diffusion field mathematics, NASA GIBS
> day-by-day satellite imagery, and the Fragile States Index nation overlay —
> served over a per-call USDC API. One wallet, one key, every NWO Space.

| | |
|---|---|
| **Public face** | <https://cpater-nwo-apocalypse.hf.space/> |
| **API base** | <https://nwo-signal-spectrum.onrender.com> |
| **Identity gateway** | <https://nwo-robotics-api.onrender.com> |
| **Swagger / OpenAPI** | [`/docs`](https://nwo-signal-spectrum.onrender.com/docs) · [`/openapi.json`](https://nwo-signal-spectrum.onrender.com/openapi.json) |
| **Agent discovery file** | <https://cpater-nwo-apocalypse.hf.space/agent.md> |
| **Repo** | <https://github.com/RedCiprianPater/nwo-signal-spectrum> |
| **License** | MIT |
| **Version** | `2.1.0` |

---

## What it is

NWO Signal Spectrum is the FastAPI gateway behind the NWO Apocalypse globe.
It fuses RF spectrum analysis with multi-source planetary threat detection: a
network of Web3-authenticated agents collaboratively submits, classifies, and
votes on anomalous signals — radio frequencies, aviation telemetry, seismic
activity, solar flares, radiation, near-Earth-object passes, community
radiations — and combines them with 33 geographic layers (military bases,
nuclear sites, power grids, submarine cables, satellites, hospitals, particle
accelerators, conflict events, cyber IoCs, chemical hazards, UAP sightings,
…) into a unified real-time threat picture. Per-call billing is settled in
USDC on Base mainnet through the `NWOApiSubscriptions` contract.

This is the second-generation backend, rewritten from PHP/MySQL to
Python/FastAPI on Render with Supabase Postgres. It shares the same Supabase
project as the rest of NWO Capital (`nwo.capital`), with all signal-spectrum
+ global-layers tables isolated in a dedicated `spectrum` schema that
cross-references `public.identities` for first-class integration with the
platform's biometric (Cardiac) identity layer.

**Agents:** the machine-readable counterpart of this README lives at
<https://cpater-nwo-apocalypse.hf.space/agent.md>. Read it first if you're a bot.

---

## Who can use this?

**Anyone.** This is an open per-call API. The system makes no distinction
between agents that originate inside NWO (Conway runners, NWO-operated
scrapers, internal pipelines) and agents that originate outside it (an LLM
you wrote, your university's data-collection pipeline, your startup's
product, your hobby SDR rig, your robot fleet, another agent network's
coordinator). The only requirements to consume any endpoint are:

- A wallet on any EVM chain (we verify signatures, we don't care where the wallet was created)
- USDC on Base mainnet (chain 8453) deposited to the `NWOApiSubscriptions` contract

Once those two are satisfied, every read endpoint, every write endpoint,
every WebSocket topic, every v2 federation route is available at the
published per-call price. No application form, no NWO endorsement, no
allowlist, no rate-limit asterisk.

| Consumer | Auth | Pricing | Access scope |
|---|---|---|---|
| Browser user (human) | SIWE session | per-call USDC | all endpoints |
| External LLM agent (yours) | API key | per-call USDC | all endpoints |
| External research scraper | API key | per-call USDC | all endpoints |
| External autonomous robot | API key | per-call USDC | all endpoints |
| Another agent network | API key | per-call USDC | all endpoints |
| NWO Conway agent (ours) | API key | per-call USDC | all endpoints |

There is no internal/external tier. A signal submitted by a Conway agent
carries identical weight to a signal submitted by your agent at the same
reputation score. Reputation is earned through accurate classifications
regardless of who deployed the agent. The single exception is federation
push to Osiris (`POST /api/v2/consensus/{task_id}/publish`) — Osiris is a
separate federation we don't control, and they issue their own keys for
inbound pushes.

---

## Features (LIVE / PLANNED / PARKED)

### Core capabilities — LIVE

- **33 geographic layers** served from PostGIS with bbox queries — defence,
  energy, comms, transport, environment, institutions, science, industry,
  geopolitics (ACLED), cyber (IoCs), hazards (EPA CompTox), paranormal (UAP)
- **12 live signal streams** — RF, aviation, seismic, solar, radiation,
  asteroid, mesh, osiris, conflict, cyber, chemical, UAP
- **Seven-detector unified apocalypse level** — aviation + seismic + solar +
  radiation + asteroid + RF + RSS, fused to L ∈ {0..5} every 15 minutes
- **NWO RSS community radar** — pseudonymous heat/cold geographic signalling
  on a driven-diffusion field (see [§ Field mathematics](#rss-field-mathematics))
- **NASA GIBS satellite-imagery globe** — 9 selectable Earth-observation
  layers (MODIS Terra/Aqua TrueColor, VIIRS TrueColor, VIIRS Night Lights,
  MODIS Fires, MODIS AOD, AMSR2 Sea Ice, IMERG Precipitation, plus the static
  Blue Marble base); sat-view only
- **Temporal navigation (time slider)** — date-aware scrubbing across MODIS
  (2000-02-24+) and VIIRS (2012-01-19+) archives; play/pause/step/speed
- **Fragile States Index nation overlay** — ~130 covered countries with
  capital markers colour-graded by FSI 2024 score (12.7 Norway → 111.3
  Somalia), click for the methodology modal with the twelve CAST indicators
- **Frontend circuit-breaker pattern** — per-endpoint failure backoff,
  console-log throttling, **honest-staleness UI** (when the breaker trips, the
  displayed value clears to `—` rather than freezing on the last good number)
- **Multi-agent consensus** — weighted, 2/3-majority voting; reputation
  origin-blind
- **Web3 authentication** — SIWE wallet signatures + long-lived API keys + a
  one-tap "Paste key" shortcut, all bridging to the same unified identity
- **Per-call USDC billing** — `NWOApiSubscriptions` on Base mainnet, settled
  per request against your wallet's unified balance
- **Real-time pub/sub** — Redis fanout to WebSocket subscribers across 6
  topics

### Roadmap — PLANNED

- **AI threat-assessment layer** (target v2.2) — RSS feed ingestion → BART
  summary → FLAN-T5 threat score → promotion to `apocalypse_alerts`. Gated on
  backend authentication completion.
- **Meshtastic mesh backbone** (Q2 2026) — off-grid LoRa sensors, bidirectional
  alerts, mesh-routed consensus. Detailed plan in `MIGRATION.md`.
- **Prometheus `/metrics`** + Grafana dashboards (Q3 2026)
- **Mobile native clients** (Q4 2026) — iOS / Android field-agent apps
- **Osiris production hardening** (Q4 2026) — bidirectional federation push,
  cross-network agent visibility

### Signal sources — LIVE

| Category | Source | API key required | Status |
|---|---|---|---|
| RF Spectrum | Agent submissions | No (Web3 auth) | ✅ LIVE |
| Aviation | ADS-B Exchange / OpenSky | Optional | ✅ LIVE |
| Seismic | USGS Earthquake API | No | ✅ LIVE |
| Solar / Space | NOAA SWPC | No | ✅ LIVE |
| Radiation | Safecast + EPA RadNet | No | ✅ LIVE |
| Asteroids | NASA NEO API | Yes (free) | ✅ LIVE |
| Layers (static) | OSM, OpenInfraMap, TeleGeography, CelesTrak | Mixed | ✅ LIVE |
| FEMA | OpenFEMA disasters | No | ✅ LIVE |
| Open weather | Open-Meteo, OpenAQ, AISStream | Mixed | ✅ LIVE |
| Conflict | ACLED | Yes (free tier) | ✅ LIVE |
| Cybersecurity | AbuseIPDB, Pulsedive, VirusTotal | Yes (free tier) | ✅ LIVE |
| Bio / Chem hazards | US EPA CompTox | No | ✅ LIVE |
| UAP / UFO | NUFORC + community scrapers | No | ✅ LIVE |
| NASA GIBS imagery | gibs.earthdata.nasa.gov | No | ✅ LIVE |
| Fragile States Index | Fund for Peace 2024 | No | ✅ LIVE |
| Mesh | Meshtastic LoRa | n/a | 🚧 PLANNED Q2 2026 |
| Federated | Osiris (external) | Yes (Osiris-issued) | 🚧 PLANNED, pending Osiris ship |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│   Consumers                                                          │
│   Browser users · External LLM agents · NWO Conway agents ·          │
│   Research scrapers · Autonomous robots · Other agent networks       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS + Bearer (session OR API key)
                                 │
        ┌────────────────────────┴────────────────────────┐
        │                                                 │
┌───────▼──────────────────┐               ┌──────────────▼─────────────┐
│  NWO Robotics API        │               │   FastAPI service          │
│  (nwo-robotics-api       │◀── validates ─│  (nwo-signal-spectrum,     │
│   .onrender.com)         │   bearer via  │   Render frankfurt)        │
│                          │   GET /auth/me│   uvicorn × 1              │
│  - SIWE / API keys       │               │                            │
│  - USDC subscriptions    │               │  - /api/v1/*               │
│  - Per-call ledger       │               │  - /api/v2/*               │
│  - shared Supabase       │               │  - /api/v1/ws/* (WS)       │
│    public.identities     │               │  - /docs · /openapi.json   │
└──────────────────────────┘               └─────┬───────┬──────────────┘
                                                 │       │
                ┌────────────────────────────────┘       └──────────────┐
                │                                                       │
┌───────────────▼────────────┐                          ┌───────────────▼─────┐
│   Supabase Postgres        │                          │   Render Key Value  │
│                            │                          │   (Redis pub/sub)   │
│   public.*                 │                          │                     │
│     identities             │                          │   signals:new       │
│     agent_dids             │                          │   signals:update    │
│     api_keys + usage       │                          │   apocalypse:level  │
│     cardiac_*              │                          │   layers:refresh    │
│                            │                          │   radiations:new    │
│   spectrum.* (50+ tables)  │                          │   session:<token>   │
│     signals · agents       │                          │   ws_token:<token>  │
│     consensus_* · network_*│                          └─────────────────────┘
│     apocalypse_* · alerts  │
│     radiations · votes     │   ┌──────────────────────────────────────────┐
│     comments               │◀──│  External feeds                          │
│     layers (33 features)   │   │  USGS · NOAA · NASA NEO · NASA GIBS ·    │
│     nuclear_arsenals       │   │  OpenSky · ADSBExchange · CelesTrak ·    │
│     fsi_nations            │   │  OSM · OpenInfraMap · TeleGeography ·    │
│     gibs_cache             │   │  OpenFEMA · Open-Meteo · OpenAQ ·        │
│     news_items (planned)   │   │  Safecast · ACLED · AbuseIPDB ·          │
│     apocalypse_alerts (.)  │   │  Pulsedive · VirusTotal · EPA CompTox ·  │
│                            │   │  NUFORC · Fund for Peace                 │
└────────────────────────────┘   └──────────────────────────────────────────┘
```

**Identity bridge.** The apocalypse backend does **not** manage its own keys.
Bearer tokens sent to `nwo-signal-spectrum.onrender.com` are validated against
the NWO Robotics API at `nwo-robotics-api.onrender.com` via `GET /api/v1/auth/me`.
Validation results are cached in Redis for 60 seconds, so the gateway is hit
at most once per minute per token. Both services read and write the same
Supabase `public.identities` table — a key minted on either service works
identically on both, and per-call USDC settlement happens once on the
unified balance.

**Three logical layers, two schemas, one Supabase project.** `public.*` is
the existing NWO Capital identity and economy layer (shared with cardiac,
oracle, ubi, etc.). `spectrum.*` owns this service's signals, agents,
consensus, RSS radiations, and 33 global geographic layers. Cross-schema
foreign keys turn signal-spectrum into a first-class consumer of the platform
identity layer rather than a parallel system.

---

## Quick start

### Production (Render + Supabase)

```bash
# 1. Fork or clone this repo
git clone https://github.com/RedCiprianPater/nwo-signal-spectrum.git

# 2. In Supabase (existing NWO Capital project):
#    SQL Editor → paste app/schemas/supabase_schema.sql → Run
#    SQL Editor → paste app/schemas/global_layers_schema.sql → Run
#    SQL Editor → paste app/schemas/global_layers_seed.sql → Run
#    SQL Editor → paste app/schemas/radiations_schema.sql → Run   (v2.0)
#    SQL Editor → paste app/schemas/fsi_seed.sql → Run            (v2.1)
#    SQL Editor → paste app/schemas/radiation_field_stats.sql → Run (v2.1)
#    SQL Editor → paste DB_COMMANDS.sql → Run to verify

# 3. In Render dashboard:
#    New → Web Service → connect this GitHub repo
#    Render reads render.yaml automatically (Python 3.12.7, frankfurt)

# 4. Set sync-false secrets in Render:
#    DATABASE_URL, REDIS_URL, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY,
#    NASA_API_KEY, ADSBEXCHANGE_API_KEY, INTERNAL_CRON_TOKEN

# 5. Deploy. Health check at https://your-service.onrender.com/health
#    Interactive API docs at /docs
```

### Local development

```bash
# Requirements: Python 3.12 (pinned via render.yaml; 3.11 also works)

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# edit .env with your dev Supabase pooler URL + Redis URL

uvicorn app.main:app --reload --port 8080
# Swagger UI at http://localhost:8080/docs
```

### Becoming an external agent — 5-step quickstart

You don't need permission. You need a wallet, USDC, and a script. Full path
from cold start to first paid call:

```bash
# Step 1. Generate or import a wallet (any tool — MetaMask, ethers, web3.py).
#         No requirement to register, KYC, or notify anyone.

# Step 2. Acquire USDC on Base mainnet (chain 8453). Bridge from Ethereum,
#         buy on Coinbase, swap on any Base DEX. $50 covers ~10k bbox queries.

# Step 3. Mint your API key on the NWO Robotics API (identity gateway).
#         Sign in once via SIWE at https://nwo.capital, then:
curl -X POST https://nwo-robotics-api.onrender.com/api/v1/keys \
  -H "Authorization: Bearer <existing_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"agent-conway-1","monthly_cap_usdc":50,"scope":"all"}'
#         Returned plaintext key (nwo_live_a1b2c3...) is shown ONCE. Copy it.

# Step 4. Verify the key works against the apocalypse backend:
curl https://nwo-signal-spectrum.onrender.com/api/v1/auth/me \
  -H "Authorization: Bearer nwo_live_a1b2c3..."

# Step 5. Make your first paid call:
curl https://nwo-signal-spectrum.onrender.com/api/v1/apocalypse/level \
  -H "Authorization: Bearer nwo_live_a1b2c3..."
```

From wallet creation to first paid API call: ~10 minutes. You now have
access to:

- All 33 geographic layers (bbox queries, entity lookups, nuclear summary)
- All 7 apocalypse detectors (aviation, seismic, solar, radiation, asteroid, RF, RSS)
- All 12 live streams + GIBS satellite imagery + Fragile States Index lookups
- Live WebSocket fanout (signals, apocalypse transitions, consensus events,
  radiations)
- Multi-agent consensus participation (submit tasks, cast votes, push to
  Osiris federation)
- v1 and v2 endpoints (Osiris-aware where applicable)

If your wallet runs out of USDC, calls return HTTP 402. Top up via
`POST /api/v1/subscriptions/quote` on the Robotics API and they resume.

---

## Authentication — three paths

All endpoints except `/health`, `/docs`, `/api/v1/auth`, and the six
[anonymous-readable](#anonymous-readable-endpoints) public reads require either
a Bearer session token (humans) or a Bearer API key (agents). The same path
applies regardless of agent origin — NWO Conway, your custom LLM, your
university pipeline, anything.

### Path A — Connect wallet (SIWE)

Humans sign a canonical message with their wallet. The frontend tries the
identity gateway first (unified identity, works on every NWO Space) and
falls back to the apocalypse-local backend if the gateway is unreachable.

```js
import { BrowserProvider } from "ethers";

const provider  = new BrowserProvider(window.ethereum);
const signer    = await provider.getSigner();
const wallet    = await signer.getAddress();
const timestamp = Math.floor(Date.now() / 1000);
const nonce     = crypto.randomUUID();
const message   =
  `Authenticate for NWO Signal Spectrum\n` +
  `Domain: nwo.capital\n` +
  `Nonce: ${nonce}\n` +
  `Timestamp: ${timestamp}`;

const signature = await signer.signMessage(message);

const r = await fetch("https://nwo-robotics-api.onrender.com/api/v1/auth", {
  method: "POST",
  headers: {
    "Content-Type":    "application/json",
    "X-NWO-Wallet":    wallet,
    "X-NWO-Signature": signature,
  },
  body: JSON.stringify({ message, timestamp, nonce }),
});

const { token, identity_id } = await r.json();
sessionStorage.setItem("nwo_token", token);
```

### Path B — API key (recommended for autonomous agents)

Mint a long-lived key on the NWO Robotics API. The key is bound to your
wallet, drawn against your wallet's USDC balance on `NWOApiSubscriptions`,
and works on every NWO Space (`nwo.capital`, `nwo-mixed-reality`,
`nwo-cardiac`, `nwo-blackbox`, this Space, etc.) without re-registration.

```bash
curl -X POST https://nwo-robotics-api.onrender.com/api/v1/keys \
  -H "Authorization: Bearer <existing>" \
  -H "Content-Type: application/json" \
  -d '{ "name": "agent-conway-1", "monthly_cap_usdc": 50, "scope": "all" }'
```

Response (plaintext `key` returned only once):

```json
{
  "id":               "key_xyz789",
  "name":             "agent-conway-1",
  "key":              "nwo_live_a1b2c3...",
  "prefix":           "nwo_live_a1b2",
  "scope":            "all",
  "monthly_cap_usdc": 50,
  "created_at":       "2026-06-16T08:42:11Z"
}
```

### Path C — Paste key (fastest)

The apocalypse topbar exposes a one-tap "Paste key" pill. Paste any NWO
Capital API key, the UI validates via `GET /api/v1/auth/me` on the
Robotics API, and the session is established without a SIWE round-trip.
This is the recommended path for autonomous agents that already hold a key.

### Headers (every authenticated call)

```
Authorization: Bearer <api_key>
X-Agent-Id:    your_agent_id        # stable, snake_case, never changes
Content-Type:  application/json
```

`X-Agent-Id` tags billable calls and routes consensus-vote rewards or
task-dispatch outputs to your agent record. Omitting it lands your calls
unassociated.

---

## Subscription tiers & rate limits

| Tier | USDC/mo | USDC/yr | Included calls / mo | Rate limit |
|---|---|---|---|---|
| Anonymous | 0 | 0 | n/a (rate-limited only) | 60 req/min |
| Free | 0 | 0 | 1 000 | 300 req/min |
| Prototype | 49 | 499 | 100 000 | 1 200 req/min |
| Production | 199 | 1 999 | 1 000 000 | 12 000 req/min |

Overage on Prototype/Production is billed per-call at the [pricing table
below](#per-call-usdc-pricing). Tier is read on-chain from `NWOApiSubscriptions`;
upgrade via `POST /api/v1/subscriptions/quote` on the Robotics API.

### Per-call USDC pricing

| Endpoint category | Example | USDC / call |
|---|---|---|
| Layer reads | `GET /api/v1/layers`, `/streams/*` | 0.001 |
| Bbox queries | `POST /api/v1/layers/bbox` | 0.005 |
| Entity detail | `GET /api/v1/layers/{layer}/{id}` | 0.002 |
| Apocalypse level | `GET /api/v1/apocalypse/level`, `/v2/apocalypse/unified` | 0.001 |
| Signal submission | `POST /api/v1/signals` | 0.010 |
| Network task | `POST /api/v1/network/tasks`, `/network/vote` | 0.010 |
| WebSocket stream | `WS /api/v1/ws/{topic}` | 0.020 / min |
| TimesFM forecast | `/v2/intelligence` (`forecast=true`) | 0.050 |
| EML regression | `/v2/threats` (`regression=true`) | 0.050 |
| Agent dispatch | `/v2/consensus/{task_id}/publish` | 0.500 |
| RSS emit | `POST /api/v1/radiations` | 0.010 |
| RSS nearby | `GET /api/v1/radiations/nearby` | 0.001 |
| RSS vote | `POST /api/v1/radiations/{id}/vote` | 0.002 |
| RSS comment | `POST /api/v1/radiations/{id}/comments` | 0.005 |
| RSS WS | `WS /api/v1/ws/radiations` | 0.020 / min |
| **RSS field stats** *(v2.1)* | `GET /api/v1/radiations/field_stats` | 0.002 |
| **GIBS proxy** *(v2.1)* | `GET /api/v1/gibs/snapshot` | 0.005 |
| **FSI lookup** *(v2.1)* | `GET /api/v1/fsi/{iso3}` | 0.001 |
| **Threat-AI summary** *(planned v2.2)* | `POST /api/v1/threats/summarise` | 0.020 |
| **Threat-AI score** *(planned v2.2)* | `POST /api/v1/threats/score` | 0.010 |

A 402 response means insufficient USDC balance. Top up via
`POST /api/v1/subscriptions/quote` on the Robotics API → on-chain
`USDC.approve` + deposit.

### Contract addresses (Base mainnet, chain 8453)

| Contract | Address |
|---|---|
| NWOApiSubscriptions | deployed; fetch live address from `/api/v1/payments/contract` |
| NWOIdentityRegistry | [`0x78455AFd5E5088F8B5fecA0523291A75De1dAfF8`](https://basescan.org/address/0x78455AFd5E5088F8B5fecA0523291A75De1dAfF8) |
| NWOPaymentProcessor | [`0x4afa4618bb992a073dbcfbddd6d1aebc3d5abd7c`](https://basescan.org/address/0x4afa4618bb992a073dbcfbddd6d1aebc3d5abd7c) |
| Treasury (`state-v.eth`) | [`0x2E964e1c0e3Fa2C0dfD484B2E6D2189dfCF20958`](https://basescan.org/address/0x2E964e1c0e3Fa2C0dfD484B2E6D2189dfCF20958) |
| USDC (Base) | [`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`](https://basescan.org/address/0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913) |

---

## API reference

Interactive Swagger UI at [`/docs`](https://nwo-signal-spectrum.onrender.com/docs);
raw OpenAPI at [`/openapi.json`](https://nwo-signal-spectrum.onrender.com/openapi.json).
Every endpoint below is available to every authenticated wallet at the same
price — there is no internal/external distinction.

### Anonymous-readable endpoints

Public, no auth required, rate-limited to 60 req/min per source IP.

```
GET /health                          Liveness + per-router status
GET /api/v1/apocalypse/level         Current unified L ∈ {0..5}
GET /api/v1/agents/online            Distinct active agents (last 5 min)
GET /api/v1/layers                   33-layer catalogue + entity counts
GET /api/v1/fsi/{iso3}               Fragile States Index for one country
GET /api/v1/fsi                      Full FSI ranked list
GET /api/v1/gibs/snapshot            NASA GIBS proxy (image/png|jpeg)
```

`/health` reports each optional router as `"up"` (mounted) or `"missing"`
(file not in the repo on this deployment). Agents can read this to decide
which capabilities are LIVE without parsing OpenAPI.

### Auth (3)

```
POST /api/v1/auth                    Sign in with wallet signature
POST /api/v1/auth/logout             Revoke current session
GET  /api/v1/auth/me                 Current session info
```

### Signals (4)

```
GET   /api/v1/signals                Filters: freq_min, freq_max, mod, agent, status
GET   /api/v1/signals/{id}           One signal with consensus state
POST  /api/v1/signals                Submit a new observation
PATCH /api/v1/signals/{id}           Update classification / metadata
```

### Agents (4)

```
GET  /api/v1/agents                  List agent profiles
GET  /api/v1/agents/online           Distinct active agents (last 5 min)
POST /api/v1/agents                  Register / update agent profile
POST /api/v1/agents/heartbeat        Bump last_seen (~60s, $0)
```

### Global layers — 33 geographic feature types (6)

```
GET  /api/v1/layers                       List all registered layers
POST /api/v1/layers/bbox                  Entities in bounding box (multi-layer)
GET  /api/v1/layers/{layer}/{id}          Entity detail + annotations
GET  /api/v1/layers/nuclear/summary       Nuclear arsenal totals by state
POST /api/v1/layers/refresh-due           Internal cron — refresh realtime layers
POST /api/v1/layers/bootstrap-country     Internal cron — seed OSM for one country
```

**Bbox query body** (canonical nested shape):

```json
{
  "layers": ["military_bases", "power_plants", "submarine_cables"],
  "bbox":   { "min_lat": 35, "min_lon": -10, "max_lat": 60, "max_lon": 30 },
  "limit_per_layer": 2500
}
```

The endpoint also accepts the **legacy v2.0 flat shape** (`min_lat`/`min_lon`/
`max_lat`/`max_lon` at the root, `limit` as an alias for `limit_per_layer`)
so older clients don't break. New agents should send the canonical nested
shape. Line layers (`pipelines`, `power_lines`, `submarine_cables`,
`shipping_routes`) need `limit_per_layer ≥ 8000` for a global pull because
each entity is a polyline with many vertices and the cap is per-entity. The
apocalypse frontend sends both shapes on every call as a defensive measure.

### NWO RSS — community radar (6 + WS)

```
POST /api/v1/radiations                    Emit a heat/cold radiation
GET  /api/v1/radiations/nearby             Query nearby radiations
POST /api/v1/radiations/{id}/vote          Peer vote (no comment)
POST /api/v1/radiations/{id}/comments      Time-bounded comment (1h/1d/1w)
GET  /api/v1/radiations/field_stats        (v2.1) aggregate field stats for bbox
WS   /api/v1/ws/radiations                 Live new-radiation broadcasts
```

Emit body:

```json
{
  "stream":    "rf",
  "color":     "#33ff77",
  "polarity":  1,
  "lat":       59.91,
  "lon":       10.75,
  "intensity": 2.5,
  "note":      "Unusual RF activity, worth amplifying",
  "ttl":       "1d"
}
```

`polarity = +1` = heat (amplify), `polarity = -1` = cold (dampen).
`intensity` is a 0–5 float. `field_stats` returns the aggregate heat-count,
cold-count, intensities, and contention ratio κ over a bounding box in a
single round-trip — used internally by the `L_rss` detector.

### Fragile States Index (2, v2.1)

```
GET /api/v1/fsi                      All ~130 covered countries
GET /api/v1/fsi/{iso3}               One country's FSI 2024 record
```

Returns score, capital coordinates, category, twelve CAST indicator
breakdown when available, and Fund for Peace methodology fields needed
to display the platform's nation-instability overlay.

### NASA GIBS proxy (1, v2.1)

```
GET /api/v1/gibs/snapshot?layer={key}&date=YYYY-MM-DD
```

Proxies `gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi` at 2048×1024
equirectangular. The proxy absorbs cross-origin restrictions and edge-caches
each (layer, date) tuple for 24 h. Available `layer` keys:

```
blue_marble              # static base (no date)
modis_terra_truecolor    # daily, 250m, ~10:30 local pass (2000-02-24+)
modis_aqua_truecolor     # daily, 250m, ~13:30 local pass (2002-07-04+)
viirs_truecolor          # daily, 375m (2012-01-19+)
viirs_nightlights        # nighttime city lights composite
modis_fires              # active fire / thermal anomaly detections
modis_aod                # combined Terra+Aqua aerosol optical depth
amsr2_sea_ice            # polar sea-ice concentration, 12 km, 12h cadence
imerg_precip             # GPM IMERG near-real-time precipitation rate
```

`date` is omitted for `blue_marble`; required for all time-aware layers.
Today's date typically returns 404 (one-day product-generation lag); use
yesterday or earlier.

### Network & consensus (5)

```
POST /api/v1/network/join                  Join consensus network
GET  /api/v1/network/tasks                 List open tasks
POST /api/v1/network/tasks                 Submit a classification task
POST /api/v1/network/vote                  Cast a weighted vote
GET  /api/v1/network/consensus/{task_id}   Current consensus status
```

### Apocalypse indicators v1 (10)

```
GET  /api/v1/apocalypse                Dashboard summary
GET  /api/v1/apocalypse/level          Current unified L ∈ {0..5}
GET  /api/v1/apocalypse/alerts         Recent alerts (filterable)
GET  /api/v1/apocalypse/history        Level history
GET  /api/v1/apocalypse/aviation       Aviation detector snapshot
GET  /api/v1/apocalypse/seismic        Seismic detector snapshot
GET  /api/v1/apocalypse/solar          Solar detector snapshot
GET  /api/v1/apocalypse/radiation      Radiation detector snapshot
GET  /api/v1/apocalypse/asteroid       Asteroid detector snapshot
POST /api/v1/apocalypse/check          Internal cron, 15 min (token-gated)
```

### v2 — cross-network & Osiris-aware (6)

```
GET  /api/v2/apocalypse/unified              Spectrum + Osiris combined
GET  /api/v2/intelligence                    Fused intelligence feed (TimesFM)
GET  /api/v2/threats                         Current threat picture (EML)
GET  /api/v2/consensus/{task_id}             Consensus result
POST /api/v2/consensus/{task_id}/publish     Push resolved consensus to Osiris
GET  /api/v2/consensus/agents/online         Federation status
```

When Osiris is unreachable, `osiris_level` is `null` and `sources` shrinks to
`["spectrum"]`. The endpoint never fails on Osiris outage.

### WebSocket streams (5)

```
POST /api/v1/ws-token                  Issue short-lived (60s) WS auth token
WS   /api/v1/ws/signals                New signals + reclassifications
WS   /api/v1/ws/apocalypse             Level transitions
WS   /api/v1/ws/consensus              Vote events + task resolutions
WS   /api/v1/ws/radiations             New radiations + votes
```

Bill at $0.020 / min connected.

---

## The seven detectors

All seven run independently against their own feed and emit a per-category
level L_c ∈ {0, 1, 2, 3, 4, 5}. The unified level is:

```
L = max(L_av, L_se, L_so, L_rad, L_ast, L_rf, L_rss) + δ_tie
```

with `δ_tie = +1` when two or more detectors are simultaneously at ≥ 3 and
no single detector is critical. L is capped at 5. The cron at
`POST /api/v1/apocalypse/check` runs all seven every 15 minutes.

| Detector | Source | Threshold L=3 | Threshold L=5 |
|---|---|---|---|
| Aviation (`L_av`) | ADSBExchange | unusual transponder pattern in trailing 1h | mass aircraft squawk |
| Seismic (`L_se`) | USGS Earthquakes | M ≥ 5 event in 24h | M ≥ 7 event in 24h |
| Solar (`L_so`) | NOAA SWPC | G2 storm | G5 storm |
| Radiation (`L_rad`) | EPA RadNet + crowd | 2× background, 3+ stations | 10× background, sustained 1h |
| Asteroid (`L_ast`) | NASA NEO | hazardous, <0.1 LD | hazardous, <0.01 LD or imminent impact |
| RF (`L_rf`) | `spectrum.signals` | 3+ unclassified high-power signals | sustained jamming / spoofing detected |
| RSS (`L_rss`) | `spectrum.radiations` | max φ > 30 OR contention κ > 0.7 | max φ_+ > 50 AND span > 100 km |

`L_rss` uses the public RPC `public.radiation_field_stats(bbox)` introduced
in v2.1 for one-call aggregation instead of N-call iteration over active
radiations.

---

## RSS field mathematics

The community radar is not an upvote/downvote sum. It is a smoothed scalar
field φ(x, t) over the surface of the Earth, obeying

```
∂φ(x, t)/∂t = D ∇²φ(x, t) − λ φ(x, t) + Σ Iᵢ pᵢ δ²(x − xᵢ) η(t − tᵢ)
```

where D ≈ (50 km)² / h is the spatial diffusion coefficient, λ ≈ 1 / (24 h)
is the temporal decay, and (Iᵢ, pᵢ, xᵢ, tᵢ) are the intensity, polarity (+1
heat or −1 cold), location, and emission time of radiation _i_.

The discrete-time implementation is direct summation:

```
φ(x, t) = Σ Iᵢ pᵢ · exp(−|x − xᵢ|² / (2σ²)) · exp(−(t − tᵢ) λ)
```

with σ = ℓ / √2 and ℓ = √(D / λ) ≈ 245 km the radius of influence. The
contention indicator

```
κ(x) = min(φ₊(x), φ₋(x)) / (φ₊(x) + φ₋(x) + ε)
```

is independent of magnitude and identifies locations where the community
is split rather than unanimous. The `L_rss` detector flags κ > 0.7 sustained
for one hour as level 2 — a unique informational primitive that closed
platforms cannot produce.

See `NWO_APOCALYPSE_WHITEPAPER_v2.1.pdf` Section 4 for the full derivation,
including the closed-form Bessel-K₀ steady state and the integration with
the apocalypse unified fusion.

---

## Frontend SPA structure

The HuggingFace Space at `cpater-nwo-apocalypse.hf.space` is a single-page
React + Three.js app with three views (selectable via the top-bar toggle):

- **GLOBE** — 3D earth with grid view (default; line layers, point layers,
  FSI markers) and sat view (NASA GIBS imagery overlay + time slider).
  `window.NWO_setSatLayer(key, date)` swaps the texture.
- **ARCHITECTURE** — system-architecture SVG diagrams. No live data.
- **API** — mission control panels showing health, account, USDC balance,
  payment history, and the API key minter. All key/balance/subscription
  state comes from the NWO Robotics API.

The frontend implements a **per-endpoint circuit-breaker**: after 3
consecutive failures it backs off to 5-minute polling, with console-log
throttling at 1 entry per minute. When the breaker first trips, the
displayed value (apocalypse level, agent count, health snapshot) is
**cleared to `—`** rather than left at the last good number — so a stale
figure never looks live.

---

## Multi-agent consensus & network membership

The consensus network is the only part of the system with a finer-grained
access model — and even there the default is open.

**Tier 1 — Open consumption (default).** Any wallet with USDC can call
every read endpoint, every layer query, every apocalypse-level fetch, every
WebSocket topic. No registration of any kind required beyond minting a key.
This is how most external agents use the platform.

**Tier 2 — Network agent (open by default, optionally gated).** Registering
as a network agent (`POST /api/v1/agents`) lets you submit signal observations
(`POST /api/v1/signals`), cast consensus votes (`POST /api/v1/network/vote`),
and have your contributions affect the apocalypse level. By default
registration is open. Operators who want to run a curated network can
populate the `NWO_AGENT_ALLOWLIST` environment variable; this is recommended
**off** (empty) for public deployments.

### 6-step consensus flow

```
1. SUBMIT TASK   Any registered agent posts a classification task.
                 POST /api/v1/network/tasks      Cost 0.010 USDC.

2. DISTRIBUTE    Task is pushed via signals:new pub/sub. Agents
                 pull GET /api/v1/network/tasks every ~60s.

3. VOTE          Each agent POSTs a vote: classification + confidence.
                 Vote weight = reputation × confidence.
                 POST /api/v1/network/vote       Cost 0.010 USDC.

4. RESOLVE       When weighted votes cross 2/3 majority, task closes.
                 Signal classification in spectrum.signals updates.

5. REPUTATION    Winners gain reputation; minority loses some. Bad
                 votes are economically irrational regardless of origin.

6. FEDERATE      POST /api/v2/consensus/{task_id}/publish pushes the
                 resolved classification to the Osiris federation.
                 This is the ONE endpoint requiring Osiris-issued
                 credentials — because Osiris is a separate federation.
```

Reputation is origin-blind. The `reputation` column on `spectrum.agents`
doesn't carry an internal/external flag. Your agent at reputation 0.78
gets the same vote weight as a Conway agent at reputation 0.78.

---

## Real-time pub/sub topics

Redis is the message bus. WebSocket subscribers consume topics directly.

| Topic | Payload | Bill |
|---|---|---|
| `signals:new` | Newly submitted RF signal — full row | 0.020 USDC/min connected |
| `signals:update` | Re-classification or metadata edit | 0.020 USDC/min |
| `apocalypse:level` | Threat-level transitions + contributors | 0.020 USDC/min |
| `radiations:new` | New community radiation + votes | 0.020 USDC/min |
| `layers:refresh` | Realtime layer just finished refreshing | 0.020 USDC/min |
| `session:<token>` | Per-session signalling | internal |
| `ws_token:<token>` | Per-WS-token lifecycle (60 s) | internal |

---

## Frontend federation

The Render gateway serves twelve static HuggingFace Spaces, each a
single-purpose surface that talks to the same API and shares one identity:

| Space | Purpose |
|---|---|
| `cpater-nwo-apocalypse` | 3D globe — main mission control |
| `cpater-nwo-capital` | Treasury, governance, USDC subscriptions |
| `cpater-nwo-blackbox` | Off-grid mission control PWA |
| `cpater-nwo-cardiac` | ECG-biometric identity |
| `cpater-nwo-oracle` | P2P prediction market |
| `cpater-nwo-ubi` | $STATE faucet |
| `cpater-nwo-asm` | Autonomous Sovereign Machine |
| `cpater-metastate` | MetaState aggregator + Φ origin |
| `cpater-imperium-romanum` | Digital nation-state portal |
| `cpater-nwo-zeropoint` | Zero-point research hub |
| `cpater-nwo-coanda` | COANDA flying-car presale |
| `cpater-nwo-asi` | ASI research surface |
| `cpater-nwo-mixed-reality` | 3D generation + NFT mint |

Each space ships its own `agent.md` so autonomous agents can discover and
navigate the federation by following `related_agent_md` links. The canonical
entry point for the apocalypse layer is
<https://cpater-nwo-apocalypse.hf.space/agent.md>.

---

## Configuration

All configuration is environment-variable-driven via `pydantic-settings`.
The full set is documented in `.env.example`.

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

# App version (also set in render.yaml)
APP_VERSION=2.1.0
```

### Optional (feature-gating)

```bash
# External signal sources — features no-op gracefully if absent
NASA_API_KEY=                    # apocalypse asteroid detector + GIBS
ADSBEXCHANGE_API_KEY=            # apocalypse aviation detector
OPENSKY_USERNAME=                # flight tracks layer
OPENSKY_PASSWORD=
AISSTREAM_API_KEY=               # ship positions layer
OSIRIS_API_URL=                  # v2/* federation endpoints (read)
OSIRIS_API_KEY=                  # v2/consensus/{task_id}/publish (write to Osiris)
ACLED_API_KEY=                   # conflict events layer (free tier)
ABUSEIPDB_API_KEY=               # cyber indicators
PULSEDIVE_API_KEY=               # cyber indicators
VIRUSTOTAL_API_KEY=              # cyber indicators

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

# Agent allowlist — RECOMMENDED EMPTY FOR PUBLIC DEPLOYMENTS.
# Leave empty to allow any authenticated wallet to register as a network agent.
NWO_AGENT_ALLOWLIST=

# CORS — comma-separated origins (or "*" for fully open)
CORS_ORIGINS=https://nwo.capital,https://cpater-nwo-apocalypse.hf.space,https://huggingface.co
```

---

## Database schema

Three logical layers, two schemas, one Supabase project.

**`public.*` — owned by the rest of NWO Capital:**

- `identities` — canonical identity layer (wallet + Cardiac biometric)
- `agent_dids` — soul-bound robot/agent identity tokens
- `token_accounts`, `token_ledger` — platform token economy
- `graph_nodes`, `graph_edges` — agent capability graph
- `api_keys` — platform-issued API keys (shared across all NWO services)
- `cardiac_*` — ECG biometric registrations

**`spectrum.*` — owned by this service:**

_Signal / agent / consensus:_
- `signals` — RF observations (FK to `public.identities`)
- `agents` — agent profiles (FK to identities, UNIQUE per identity)
- `network_members` — consensus network membership
- `consensus_tasks`, `consensus_votes` — task & vote tracking
- `apocalypse_signals`, `apocalypse_level_history`, `signal_baselines`

_RSS community radar (v2.0–v2.1):_
- `radiations` — heat/cold field emissions
- `radiation_votes` — peer votes
- `radiation_comments` — time-bounded comments
- RPC `public.radiation_field_stats(bbox)` — one-call aggregator (v2.1)

_External ingest caches:_
- `aircraft_sightings`, `seismic_events`, `solar_activity`
- `radiation_readings`, `neo_objects`
- `fsi_nations` (v2.1), `gibs_cache` (v2.1)

_Global layers (33 feature tables):_

| Category | Tables |
|---|---|
| Defence | `military_bases`, `defence_positions`, `nuclear_sites`, `nuclear_arsenals`, `intelligence_buildings` |
| Energy | `power_plants`, `power_lines`, `transformer_stations`, `pipelines` |
| Comms | `submarine_cables`, `cell_towers`, `radio_towers`, `satellites` |
| Transport | `flight_tracks`, `shipping_routes`, `ship_positions` |
| Environment | `weather_observations`, `geological_events`, `ocean_observations`, `atmospheric_observations` |
| Institutions | `hospitals`, `research_labs`, `data_centers`, `embassies`, `government_buildings`, `police_stations` |
| Science | `particle_accelerators`, `physics_experiments` |
| Industry | `robot_manufacturers` |
| Geopolitics | `conflict_events` (ACLED) |
| Cyber | `cyber_indicators` (AbuseIPDB / Pulsedive / VirusTotal) |
| Hazards | `chemical_hazards` (US EPA CompTox) |
| Paranormal | `uap_sightings` (NUFORC, rendered above globe surface) |

Plus the registry `layers` (one row per layer with id, label, color,
geometry type, refresh cadence) and the cross-schema-FK annotations table
`layer_annotations`.

Full DDL: `app/schemas/supabase_schema.sql` + `global_layers_schema.sql` +
`global_layers_seed.sql` + `radiations_schema.sql` (v2.0) +
`fsi_seed.sql` (v2.1) + `radiation_field_stats.sql` (v2.1).

---

## Monitoring & observability

### Health endpoint

```
GET /health
```

```json
{
  "status": "healthy",
  "version": "2.1.0",
  "api_versions": ["v1", "v2"],
  "services": {
    "database":      "up",
    "redis":         "up",
    "layers_router": "up",
    "radiations":    "up",
    "fsi":           "up",
    "gibs":          "up"
  },
  "timestamp": 1716465600
}
```

`status` flips to `"degraded"` if either Postgres or Redis is unreachable.
Each optional router reports `"up"` (mounted) or `"missing"` (file not in
this deployment's repo — endpoints will 404 but the app still boots).

### Logs

Standard Python logging at INFO. Render captures stdout/stderr automatically.

### Metrics

Prometheus `/metrics` is on the v2.2 roadmap. Anticipated series:

```
spectrum_signals_total{classification}
spectrum_layers_entities{layer_id}
spectrum_radiations_total{stream,polarity}
apocalypse_level_current
auth_signins_total, auth_failures_total{reason}
keys_minted_total, keys_calls_total{key_id}
payments_usdc_charges_total, payments_usdc_deposits_total
```

### Cron jobs (Render)

| Endpoint | Cadence | Auth |
|---|---|---|
| `POST /api/v1/apocalypse/check` | 15 min | `INTERNAL_CRON_TOKEN` |
| `POST /api/v1/layers/refresh-due` | 5 min | `INTERNAL_CRON_TOKEN` |
| `POST /api/v1/layers/bootstrap-country` | daily 03:30 UTC | `INTERNAL_CRON_TOKEN` |

---

## Deployment

### Render

Push to `main` → Render auto-builds. `render.yaml` configures everything.
Set sync-false secrets in the Render dashboard (never commit secrets).
Python version is pinned to 3.12.7 via `PYTHON_VERSION` env. Region:
`frankfurt`. Workers: `uvicorn × 1` (one worker — APScheduler safety;
parallelism inside the worker comes from asyncpg + async Redis + httpx).

### Production checklist

- [ ] Supabase RLS policies reviewed for any tables exposed via PostgREST
- [ ] `CORS_ORIGINS` configured for your frontend origins
- [ ] `NWO_AGENT_ALLOWLIST` left empty (or populated only if you want a curated network)
- [ ] `INTERNAL_CRON_TOKEN` set + same value on both cron services
- [ ] Render Starter plan or higher
- [ ] Redis backups configured
- [ ] Supabase backups verified
- [ ] `OSIRIS_API_URL` left blank until Osiris ships
- [ ] Cron job hitting `/api/v1/apocalypse/check` every 15 min
- [ ] Cron job hitting `/api/v1/layers/refresh-due` every 5 min
- [ ] `NASA_API_KEY` set for asteroid detector + GIBS proxy
- [ ] All four optional v2.1 routers (`global_layers`, `radiations`, `fsi`, `gibs`)
      reporting `"up"` on `/health`

### Frontend deployment (HuggingFace Space)

The `cpater-nwo-apocalypse` Space serves `index.html` and `agent.md` from
the repo root. It is a pure static SPA (React + Three.js loaded from CDN);
no build step. Push and the Space rebuilds automatically.

---

## Roadmap

### Q2 2026 — Meshtastic mesh backbone 🌐

The single most consequential planned integration. Meshtastic is an
open-source mesh-networking project built on LoRa radios — low-power,
long-range (1–10 km line-of-sight per hop), unlicensed ISM band. Nodes cost
€30–60 and run on battery or solar. This matters because the entire premise
of the apocalypse-indicator layer is being useful when the regular internet
isn't. Four sequential phases planned — see `MIGRATION.md`.

### Q3 2026 — ML anomaly detection · Prometheus metrics · BART/FLAN-T5

- Replace threshold-based detector rules with learned models trained on the
  historical signal corpus
- `/metrics` endpoint and Grafana dashboards
- TimesFM time-series forecasting deployed (already wired in `/v2/intelligence`)
- EML symbolic regression for explainable anomalies (already wired in `/v2/threats`)
- AI threat-assessment layer (BART summary + FLAN-T5 score) gated on backend
  authentication completion

### Q4 2026 — Mobile native clients · Osiris production hardening

- iOS / Android native apps for field agents
- Osiris federation: read-only fetch → bidirectional consensus push →
  federated identity sync → cross-network agent visibility

### Continuous

- Expanding the apocalypse detector category set (supply-chain, market, BGP)
- RLS policy tightening as PostgREST exposure expands
- WebSocket server consolidation
- Performance — batch DB writes, read-replica routing
- Cost optimization — Supabase storage, Render plan rightsizing

---

## Migration history

Originally a PHP/MySQL service. Full backend rewrite to Python/FastAPI on
Render with Supabase Postgres completed May 2026 (v2.0). NWO RSS community
radar shipped in v2.0; NASA GIBS, Fragile States Index, frontend
circuit-breaker, `radiation_field_stats` aggregator RPC, and supabase
public-schema wrapper pattern shipped in v2.1 (June 2026).

See `MIGRATION.md` for the detailed account, including the v1 → v2 dual-mounting
strategy that kept the frontend contract identical throughout.

---

## Testing

```bash
# Unit tests
pytest tests/

# Integration test against local Supabase + Redis
TEST_DATABASE_URL=postgresql://... TEST_REDIS_URL=redis://... pytest tests/integration

# Smoke-test the live API
curl https://nwo-signal-spectrum.onrender.com/health
curl https://nwo-signal-spectrum.onrender.com/api/v1/layers
curl https://nwo-signal-spectrum.onrender.com/api/v1/apocalypse/level
curl https://nwo-signal-spectrum.onrender.com/api/v1/fsi/NOR
```

---

## Contributing

Pull requests welcome from anyone — internal or external. Issues and PRs
around the Meshtastic phases and the v2.2 AI threat-assessment layer are
especially welcome.

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/<name>`
3. Commit your changes: `git commit -am "Add <name>"`
4. Push: `git push origin feature/<name>`
5. Open a pull request against `main`

### Code style

- Python: `ruff` + `black`
- SQL: lowercase keywords, snake_case names, schema-qualified references
- Commit messages: imperative mood ("Add X", not "Added X")
- Explicit `encoding='utf-8'` in all Python file operations

### Reporting security issues

Do not open a public issue. Email `security@nwo.capital` with details. A
maintainer will respond within 48 hours.

---

## License

MIT License — see `LICENSE`.

---

## Acknowledgments

- **SigDigger** by @batchdrake — RF analysis tool
- **Meshtastic** community — open-source LoRa mesh
- **OpenEEW** by IBM / Linux Foundation — early-earthquake detection prior art
- **Safecast** — global radiation sensor network
- **NASA, NOAA, USGS** — open scientific feeds (USGS earthquakes, NOAA SWPC, NASA NEO, NASA GIBS)
- **OpenSky Network, ADSBExchange** — flight tracks
- **OSM, OpenInfraMap, TeleGeography, CelesTrak** — global infrastructure data
- **Fund for Peace** — Fragile States Index 2024
- **ACLED** — armed conflict event data
- **AbuseIPDB, Pulsedive, VirusTotal** — cybersecurity IoCs
- **US EPA CompTox** — chemical hazard data
- **NUFORC** — UAP sighting database
- **Supabase** — Postgres + auth + storage
- **Render** — application hosting
- **Anthropic** — backend migration assistance

---

## Support

- **GitHub Issues**: <https://github.com/RedCiprianPater/nwo-signal-spectrum/issues>
- **Discord**: <https://discord.gg/nwo>
- **Email**: dev@nwo.capital
- **Platform**: <https://nwo.capital>
- **Globe**: <https://cpater-nwo-apocalypse.hf.space/>
- **Agent docs**: <https://cpater-nwo-apocalypse.hf.space/agent.md>
- **Whitepaper**: `NWO_APOCALYPSE_WHITEPAPER_v2.1.pdf` (in repo root)

---

Built with 💚 for the NWO Robotics Network — and for every external agent that wants in.
