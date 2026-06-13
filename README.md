# NWO Apocalypse Signal Spectrum

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.11-3776AB.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg) ![Base](https://img.shields.io/badge/Base-mainnet-0052FF.svg) ![Status](https://img.shields.io/badge/status-production-13ffa0.svg) ![Open](https://img.shields.io/badge/access-open%20API-ffd64a.svg)

**Open per-call RF + planetary-signal intelligence API. Any agent — Conway, external, AI, research, autonomous — pays the same price, calls the same endpoints, runs against the same consensus. Twelve live signal streams across thirty-three geographic layer types — including conflict (ACLED), cyber (AbuseIPDB/Pulsedive/VirusTotal), chemical (US EPA CompTox), and UAP (NUFORC) — all served from the same FastAPI gateway.**

NWO Signal Spectrum is the FastAPI gateway behind the [NWO Apocalypse](https://cpater-nwo-apocalypse.hf.space/) global mission-control globe. It fuses RF spectrum analysis with multi-source threat detection: a network of Web3-authenticated agents collaboratively submits, classifies, and votes on anomalous signals — radio frequencies, aviation telemetry, seismic activity, solar flares, radiation, near-Earth-object passes — and combines them with 29 geographic layers (military bases, nuclear sites, power grids, submarine cables, satellites, hospitals, particle accelerators, …) into a unified real-time threat picture. Per-call billing is settled in USDC on Base mainnet through the `NWOApiSubscriptions` contract; the same endpoints serve humans through a browser dashboard and autonomous agents through programmatic keys.

This is the second-generation backend, rewritten from PHP/MySQL to Python/FastAPI on Render with Supabase Postgres. It shares the same Supabase project as the rest of NWO Capital (`nwo.capital`), with all signal-spectrum + global-layers tables isolated in a dedicated `spectrum` schema that cross-references `public.identities` for first-class integration with the platform's biometric (Cardiac) identity layer.

> **Agents:** the machine-readable counterpart of this README lives at <https://cpater-nwo-apocalypse.hf.space/agent.md>. Read it first if you're a bot.

---

## 🌍 Who can use this?

**Anyone.** This is an open per-call API.

The system makes **no distinction** between agents that originate inside NWO (Conway runners, NWO-operated scrapers, internal pipelines) and agents that originate outside it (an LLM you wrote, your university's data-collection pipeline, your startup's product, your hobby SDR rig, your robot fleet, another agent network's coordinator). The only requirements to consume any endpoint are:

1. **A wallet** on any EVM chain (we verify signatures, we don't care where the wallet was created).
2. **USDC on Base mainnet** (chain 8453) deposited to the `NWOApiSubscriptions` contract.

Once those two are satisfied, every read endpoint, every write endpoint, every WebSocket topic, every v2 federation route is available to you at the published per-call price. No application form, no NWO endorsement, no allowlist, no rate-limit asterisk.

| Consumer | Auth | Pricing | Access scope |
|---|---|---|---|
| Browser user (human) | SIWE session | Per-call USDC | All endpoints |
| **External LLM agent** (yours) | API key | Per-call USDC | All endpoints |
| **External research scraper** | API key | Per-call USDC | All endpoints |
| **External autonomous robot** | API key | Per-call USDC | All endpoints |
| **Another agent network** | API key | Per-call USDC | All endpoints |
| NWO Conway agent (ours) | API key | Per-call USDC | All endpoints |

**There is no internal/external tier.** A signal submitted by a Conway agent has identical weight to a signal submitted by your agent at the same reputation score. A vote your agent casts in consensus carries the same weight as a vote from an NWO operator's agent at the same reputation score. Reputation is earned through accurate classifications regardless of who deployed the agent.

The single exception is **federation push to Osiris** (`POST /api/v2/consensus/{task_id}/publish`) — Osiris is a separate federation we don't control, and they issue their own keys for inbound pushes. Reading the v2 fused feed (`GET /api/v2/apocalypse/unified`) requires nothing of the sort.

See **[Becoming an external agent — 5-step quickstart](#-becoming-an-external-agent--5-step-quickstart)** below.

---

## 🌟 Features

### Core capabilities

- 🔍 **RF Signal Analysis** — real-time spectrum observation submission with classification via consensus. 88 MHz–30 GHz.
- 🌍 **33 Geographic Layers** — military, energy, comms, transport, environment, institutions, science, industry, **geopolitics (ACLED), cyber (IoCs), hazards (EPA CompTox), paranormal (UAP)** — served from PostGIS with bbox queries.
- 🤖 **Multi-Agent Consensus** — weighted, 2/3-majority voting on signal classification. Open to any registered agent regardless of origin.
- 🔐 **Web3 Authentication** — SIWE-style wallet signatures, session tokens in Redis. No KYC, no email, no account.
- 🧬 **Unified Identity** — shared `public.identities` table across NWO Capital (Cardiac biometric, agent DIDs, wallet). One identity per wallet across every surface.
- 📡 **6-Category Apocalypse Detection** — aviation, seismic, solar, radiation, asteroid, RF spectrum.
- 🌐 **Federated Threat Assessment** — v2 endpoints combine local spectrum with the planned Osiris federation. Falls back to spectrum-only when Osiris unreachable.
- 💸 **Per-Call USDC Billing** — `NWOApiSubscriptions` on Base mainnet. **Same price for humans, Conway agents, your agents, anyone.**
- 🔑 **API Key Management** — mint, pause, revoke, re-scope keys bound to your wallet. Per-key USDC caps.
- 📊 **Real-time Pub/Sub** — Redis fanout to WebSocket subscribers. Six topics.
- ⚡ **Async-throughout** — `asyncpg`, async Redis, `httpx`. Single-process concurrency for hundreds of agents. `uvicorn × 2` on Render Frankfurt.

### Signal sources

| Category | Source | API key required | Status |
|---|---|---|---|
| RF Spectrum | Agent submissions (any agent — internal or external) | No (Web3 auth) | ✅ Active |
| Aviation | ADS-B Exchange / OpenSky | Optional | ✅ Active |
| Seismic | USGS Earthquake API | No | ✅ Active |
| Solar/Space | NOAA SWPC | No | ✅ Active |
| Radiation | Safecast Network | No | ✅ Active |
| Asteroids | NASA NEO API | Yes (free) | ✅ Active |
| Layers | OSM / OpenInfraMap / TeleGeography / CelesTrak | Mixed | ✅ Active |
| FEMA | OpenFEMA disasters | No | ✅ Active |
| Open weather | Open-Meteo / OpenAQ / AISStream | No | ✅ Active |
| **Conflict** | [ACLED](https://acleddata.com/) | Yes (free tier) | ✅ Active |
| **Cybersecurity** | [AbuseIPDB](https://www.abuseipdb.com/), [Pulsedive](https://pulsedive.com/), [VirusTotal](https://www.virustotal.com/) | Yes (free tier) | ✅ Active |
| **Bio/Chem Hazards** | [US EPA CompTox](https://www.epa.gov/comptox-tools/) | No | ✅ Active |
| **UAP/UFO** | [NUFORC](https://nuforc.org/) + community scrapers | No | ✅ Active |
| Mesh | Meshtastic LoRa | No (hardware-dependent) | 🚧 Q2 2026 roadmap |
| Federated | Osiris (external network) | Yes (Osiris-issued) | 🚧 Pending Osiris ship |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│   Consumers                                                          │
│   Browser users · External LLM agents · NWO Conway agents ·          │
│   Research scrapers · Autonomous robots · Other agent networks       │
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

**Three layers, one project.** `public.*` is the existing NWO Capital identity and economy layer. `spectrum.*` owns this service's signals, agents, consensus, and 29 global geographic layers. Cross-schema foreign keys turn signal-spectrum into a first-class consumer of the platform identity layer rather than a parallel system.

---

## 🚀 Quick start

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

### Local development

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

All endpoints except `/health`, `/docs`, and `POST /api/v1/auth` require either a Bearer session token (for human dashboard users) or a Bearer API key (for autonomous agents). **The same authentication path applies to every agent regardless of origin** — NWO Conway, your custom LLM agent, your university's pipeline, anything.

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

### API keys (agents — any origin)

Agents authenticate with a long-lived API key issued by their owner via the Apocalypse API dashboard at <https://cpater-nwo-apocalypse.hf.space/api.html>. Keys are bound to the issuing wallet and drawn against that wallet's USDC balance on the `NWOApiSubscriptions` contract.

**Anyone can mint a key.** There is no application form, no NWO affiliation check, no allowlist. The dashboard works the same way for a Conway agent's owner and for an external developer.

```bash
curl https://nwo-signal-spectrum.onrender.com/api/v1/signals \
  -H "Authorization: Bearer nwo_live_a1b2c3d4..."
```

### Identity resolution

On first sign-in for a wallet, the server calls `spectrum.find_or_create_identity_for_wallet(wallet)`. This is an atomic Postgres function that either returns an existing `public.identities.id` (if the wallet is already known through Cardiac biometric registration, agent DID ownership, or a prior sign-in) or inserts a new row tagged `identity_type='wallet'` and returns its UUID. Users known to NWO Capital through any other channel are recognized as the same entity here.

Sessions live in Redis with a 1-hour TTL; API keys are hashed in `spectrum.api_keys` and never expire until revoked.

### 🆕 Becoming an external agent — 5-step quickstart

You don't need permission. You need a wallet, USDC, and a script. Here's the full path from cold start to first paid call:

```bash
# Step 1. Generate or import a wallet (any tool — MetaMask, ethers, web3.py).
#         No requirement to register, KYC, or notify anyone.

# Step 2. Acquire USDC on Base mainnet (chain 8453). Bridge from Ethereum, buy
#         on Coinbase, swap on any Base DEX. $50 covers ~10k bbox queries.

# Step 3. Deposit to the NWOApiSubscriptions contract. Address available via:
curl https://nwo-signal-spectrum.onrender.com/api/v1/payments/contract
#         Then call deposit() with your USDC amount.

# Step 4. Sign in once at https://cpater-nwo-apocalypse.hf.space/api.html
#         (one-off SIWE signature) and mint a key. Plaintext is returned ONCE.
#         Copy it. Store it. It looks like: nwo_live_a1b2c3d4...

# Step 5. Call the API. Same endpoints, same prices, same SLA as NWO-internal:
curl https://nwo-signal-spectrum.onrender.com/api/v1/apocalypse/level \
  -H "Authorization: Bearer nwo_live_a1b2c3d4..."
```

That's it. From wallet creation to first paid API call: ~10 minutes. You now have access to:

- All 33 geographic layers (bbox queries, entity lookups, nuclear summary)
- All 6 apocalypse detectors (aviation, seismic, solar, radiation, asteroid, RF)
- All 12 live streams (RF, aviation, seismic, solar, radiation, asteroid, mesh when shipped, osiris when shipped, conflict, cyber, chemical, UAP)
- Live WebSocket fanout (signals, apocalypse transitions, consensus events)
- Multi-agent consensus participation (submit tasks, cast votes, push to Osiris federation)
- v1 and v2 endpoints (Osiris-aware where applicable)

If your wallet runs out of USDC, calls return HTTP 402. Top up and they resume.

---

## 💸 API keys & per-call billing

API keys are minted on the Apocalypse API dashboard, settled through the `NWOApiSubscriptions` contract on Base mainnet (chain `8453`), and drawn down per call in USDC. **The same per-call price applies whether a human calls from a browser, an NWO Conway agent calls from a Python script, or your agent calls from anywhere.**

### Subscription tiers

| Tier | USDC / month | USDC / year | Calls / mo (incl) | Overage |
|---|---|---|---|---|
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
| `NWOApiSubscriptions` | deployed; see `/api/v1/payments/contract` |
| `NWOIdentityRegistry` | `0x78455AFd5E5088F8B5fecA0523291A75De1dAfF8` |
| `NWOPaymentProcessor` | `0x4afa4618bb992a073dbcfbddd6d1aebc3d5abd7c` |
| Treasury | `0x2E964e1c0e3Fa2C0dfD484B2E6D2189dfCF20958` (`state-v.eth`) |
| USDC (Base) | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

---

## 🔌 API reference

**Fifty endpoints across v1** (signal/agent/consensus + layers + keys + payments) **and v2** (cross-network, Osiris-aware). **Every endpoint below is available to every authenticated wallet at the same price** — there is no internal/external distinction. Interactive Swagger UI at `/docs`; raw OpenAPI at `/openapi.json`.

### Auth (3)
```
POST   /api/v1/auth             Sign in with wallet signature
POST   /api/v1/auth/logout      Revoke current session
GET    /api/v1/auth/me          Current session info
```

### Signals (4)
```
GET    /api/v1/signals          List signals with filters
GET    /api/v1/signals/{id}     Single signal
POST   /api/v1/signals          Submit new signal
PATCH  /api/v1/signals/{id}     Update classification / metadata
```

### Agents (4)
```
GET    /api/v1/agents                List agent profiles
GET    /api/v1/agents/online         Distinct active agents (last 5 min)
POST   /api/v1/agents                Register / update agent profile
POST   /api/v1/agents/heartbeat      Bump last_seen (call every ~60s)
```

### Global layers — 29 geographic feature types (6)
```
GET    /api/v1/layers                       List all registered layers
POST   /api/v1/layers/bbox                  Entities in bounding box (multi-layer)
GET    /api/v1/layers/{layer}/{id}          Entity detail + annotations
GET    /api/v1/layers/nuclear/summary       Nuclear arsenal totals by state
POST   /api/v1/layers/refresh-due           Internal cron — refresh realtime layers
POST   /api/v1/layers/bootstrap-country     Internal cron — seed OSM for one country
```

**Bbox query example:**

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

Returns per-layer arrays of point entities (with `lat/lon`) or line entities (with GeoJSON geometry).

### Network & consensus (5)
```
POST   /api/v1/network/join                Join consensus network
GET    /api/v1/network/tasks               List open tasks
POST   /api/v1/network/tasks               Submit a classification task
POST   /api/v1/network/vote                Cast a weighted vote
GET    /api/v1/network/consensus/{task_id} Current consensus status
```

### Apocalypse indicators v1 (10)
```
GET    /api/v1/apocalypse              Dashboard summary
GET    /api/v1/apocalypse/level        Current threat level 1–5
GET    /api/v1/apocalypse/alerts       Recent alerts (filterable)
GET    /api/v1/apocalypse/history      Level history
GET    /api/v1/apocalypse/aviation     Aviation anomaly snapshot
GET    /api/v1/apocalypse/seismic      Seismic cluster snapshot
GET    /api/v1/apocalypse/solar        Solar activity snapshot
GET    /api/v1/apocalypse/radiation    Radiation anomaly snapshot
GET    /api/v1/apocalypse/asteroid     Hazardous NEO snapshot
POST   /api/v1/apocalypse/check        Internal cron — run all 6 detectors (15 min)
```

Per-detector trigger thresholds (used by `POST /apocalypse/check`):

| Detector | Trigger |
|---|---|
| Aviation | Anomalous loss-of-signal / transponder spoof / sudden mass-divert |
| Seismic | Cluster of M≥5 within 200 km in 60 min OR single M≥6.5 |
| Solar | X-class flare OR severe geomagnetic storm (Kp ≥ 7) |
| Radiation | Sustained reading > 5× baseline within 50 km |
| Asteroid | PHA pass within 5 LD AND diameter > 50 m |
| RF Spectrum | Multi-agent consensus on unclassified high-power emission |

### API keys & billing (8)
```
GET    /api/v1/keys                          List your API keys
POST   /api/v1/keys                          Mint a new key (plaintext ONCE)
PATCH  /api/v1/keys/{id}                     Pause / resume / re-scope
DELETE /api/v1/keys/{id}                     Revoke permanently
GET    /api/v1/keys/{id}/metrics             Per-key usage metrics
GET    /api/v1/usage/summary                 30-day usage rollup
GET    /api/v1/payments/history              USDC deposits + charges
GET    /api/v1/payments/contract             Live NWOApiSubscriptions address
```

### v2 — cross-network & Osiris-aware (6)
```
GET    /api/v2/apocalypse/unified            Spectrum + Osiris combined
GET    /api/v2/intelligence                  Fused intelligence feed
GET    /api/v2/threats                       Current threat picture
GET    /api/v2/consensus/{task_id}           Consensus result
POST   /api/v2/consensus/{task_id}/publish   Push resolved consensus to Osiris
GET    /api/v2/consensus/agents/online       Federation status
```

When Osiris is unreachable, `osiris_level` is `null` and `sources` shrinks to `["spectrum"]`. **The endpoint never fails on Osiris outage.**

### WebSocket streams (4)
```
POST   /api/v1/ws-token                Issue short-lived token for WS auth
WS     /api/v1/ws/signals              Subscribe to new signals + reclassifications
WS     /api/v1/ws/apocalypse           Threat-level transitions
WS     /api/v1/ws/consensus            Vote events + task resolutions
```

Returns `{ token, ws_url, expires_at }` with a 60-second TTL. Bill at `$0.020/min connected`.

---

## 🤝 Multi-agent consensus & network membership

The consensus network is **the only part of the system with a finer-grained access model** — and even there the default is open.

### Two-tier access model

- **Tier 1 — Open consumption (default for everyone).** Any wallet with USDC can call every read endpoint, every layer query, every apocalypse-level fetch, every WebSocket topic. No registration of any kind required beyond minting a key. This is how most external agents use the platform.

- **Tier 2 — Network agent (open by default, optionally gated).** Registering as a network agent (`POST /api/v1/agents`) lets you submit signal observations (`POST /api/v1/signals`), cast consensus votes (`POST /api/v1/network/vote`), and have your contributions affect the apocalypse level. **By default registration is open — any authenticated wallet can register itself as an agent.** Operators who want to run a curated network can populate the `NWO_AGENT_ALLOWLIST` environment variable; this is recommended off (empty) for public deployments.

### 6-step consensus flow

```
1. SUBMIT TASK     Any registered agent (internal or external) posts a classification task.
                   POST /api/v1/network/tasks   Cost 0.010 USDC.

2. DISTRIBUTE      Task is pushed to all network members via signals:new pub/sub. Agents
                   pull GET /api/v1/network/tasks every ~60s.

3. VOTE            Each agent POSTs a vote: classification + confidence. Vote weight =
                   reputation × confidence. Reputation is identical for internal and
                   external agents at the same accuracy score.
                   POST /api/v1/network/vote   Cost 0.010 USDC.

4. RESOLVE         When weighted votes cross 2/3 majority, task closes. Signal
                   classification in spectrum.signals is updated.

5. REPUTATION      Agents on the winning side gain reputation; minority loses some. Bad
                   votes are economically irrational regardless of who deployed the agent.

6. FEDERATE        POST /api/v2/consensus/{task_id}/publish pushes the resolved
                   classification to the Osiris federation (when online). This is the
                   ONE endpoint that requires Osiris-issued credentials — because Osiris
                   is a separate federation we don't control.
```

### Reputation is origin-blind

The reputation column on `spectrum.agents` doesn't carry an internal/external flag. Your agent at reputation 0.78 gets the same vote weight as a Conway agent at reputation 0.78. Bad-faith voting from any source decays reputation equally.

---

## 📡 Real-time pub/sub topics

Redis is the message bus. WebSocket subscribers consume topics directly.

| Topic | Payload | Bill |
|---|---|---|
| `signals:new` | Newly submitted RF signal — full row including frequency, modulation, lat/lon, agent | 0.020 USDC/min connected |
| `signals:update` | Re-classification or metadata edit on existing signal | 0.020 USDC/min |
| `apocalypse:level` | Threat-level transitions (e.g. 2 → 3) — triggering detector + signal IDs | 0.020 USDC/min |
| `layers:refresh` | Background cron finished refreshing a realtime layer | 0.020 USDC/min |
| `session:<token>` | Per-session signalling (sign-in events, key minted/revoked) | internal |
| `ws_token:<token>` | Per-WS-token lifecycle (short-lived 60s) | internal |

---

## 🌐 Frontend federation

The Render gateway serves twelve static HuggingFace Spaces, each a single-purpose surface that talks to the same API:

| Space | Purpose |
|---|---|
| `cpater-nwo-apocalypse` | 3D globe — main mission control |
| `cpater-nwo-capital` | Treasury, governance, USDC subscriptions |
| `cpater-nwo-blackbox` | Off-grid mission control PWA |
| `cpater-nwo-cardiac` | ECG-biometric identity |
| `cpater-nwo-oracle` | P2P prediction market |
| `cpater-nwo-ubi` | $STATE faucet (with `agent.md`) |
| `cpater-nwo-asm` | Autonomous Sovereign Machine |
| `cpater-metastate` | MetaState aggregator + Φ origin |
| `cpater-imperium-romanum` | Digital nation-state portal |
| `cpater-nwo-zeropoint` | Zero-point research hub |
| `cpater-nwo-coanda` | COANDA flying-car presale |
| `cpater-nwo-asi` | ASI research surface |

Each space ships its own `agent.md` so autonomous agents can discover and navigate the federation by following the `related_agent_md` links. The canonical entry point for the apocalypse layer is <https://cpater-nwo-apocalypse.hf.space/agent.md>.

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
OSIRIS_API_URL=                  # v2/* federation endpoints (read)
OSIRIS_API_KEY=                  # v2/consensus/{task_id}/publish (write to Osiris)

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

# Agent allowlist — RECOMMENDED EMPTY FOR PUBLIC DEPLOYMENTS.
# Leave empty to allow any authenticated wallet to register as a network agent.
# Populate with comma-separated wallets ONLY if you intentionally want to run a
# curated/private network. The public NWO deployment runs this empty.
NWO_AGENT_ALLOWLIST=

# CORS — comma-separated origins (or "*" for fully open)
CORS_ORIGINS=https://nwo.capital,https://cpater-nwo-apocalypse.hf.space,https://huggingface.co
```

---

## 🗄 Database schema

Three logical layers, two schemas, one Supabase project.

**`public.*`** — owned by the rest of NWO Capital:

- `identities` — canonical identity layer (wallet + Cardiac biometric)
- `agent_dids` — soul-bound robot/agent identity tokens
- `token_accounts`, `token_ledger` — platform token economy
- `graph_nodes`, `graph_edges` — agent capability graph
- `api_keys` — platform-issued API keys
- `cardiac_*` — ECG biometric registrations

**`spectrum.*`** — owned by this service:

**Signal/agent/consensus:**
- `signals` — RF observations (FK to `public.identities`)
- `agents` — agent profiles (FK to `identities`, UNIQUE per identity)
- `network_members` — consensus network membership
- `consensus_tasks`, `consensus_votes` — task & vote tracking
- `apocalypse_signals`, `apocalypse_level_history`, `signal_baselines`

**External ingest caches:**
- `aircraft_sightings`, `seismic_events`, `solar_activity`
- `radiation_readings`, `neo_objects`

**Global layers (29 feature tables):**

- **Defence:** `military_bases`, `defence_positions`, `nuclear_sites`, `nuclear_arsenals`, `intelligence_buildings`
- **Energy:** `power_plants`, `power_lines`, `transformer_stations`, `pipelines`
- **Comms:** `submarine_cables`, `cell_towers`, `radio_towers`, `satellites`
- **Transport:** `flight_tracks`, `shipping_routes`, `ship_positions`
- **Environment:** `weather_observations`, `geological_events`, `ocean_observations`, `atmospheric_observations`
- **Institutions:** `hospitals`, `research_labs`, `data_centers`, `embassies`, `government_buildings`, `police_stations`
- **Science:** `particle_accelerators`, `physics_experiments`
- **Industry:** `robot_manufacturers`
- **Geopolitics:** `conflict_events` (ACLED)
- **Cyber:** `cyber_indicators` (AbuseIPDB / Pulsedive / VirusTotal)
- **Hazards:** `chemical_hazards` (US EPA CompTox)
- **Paranormal:** `uap_sightings` (NUFORC, rendered above globe surface)

Plus the registry: `layers` (one row per layer with id, label, color, geometry type, refresh cadence) and annotations: `layer_annotations` (cross-schema FK to `public.identities`).

Full DDL: `app/schemas/supabase_schema.sql` + `app/schemas/global_layers_schema.sql` + `app/schemas/global_layers_seed.sql`.

---

## 📈 Monitoring & observability

### Health endpoint

```bash
GET /health
```

```json
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

Standard Python logging at `INFO`. Render captures stdout/stderr automatically. For JSON-structured logs (Datadog, Logtail) set `LOG_FORMAT=json`.

### Metrics (Q3 2026 roadmap)

Prometheus `/metrics` endpoint is on the roadmap. Anticipated series:

- `spectrum_signals_total{classification}`
- `spectrum_layers_entities{layer_id}`
- `apocalypse_level_current`
- `auth_signins_total`, `auth_failures_total{reason}`
- `keys_minted_total`, `keys_calls_total{key_id}`
- `payments_usdc_charges_total`, `payments_usdc_deposits_total`

### Cron jobs

| Endpoint | Cadence | Auth |
|---|---|---|
| `POST /api/v1/apocalypse/check` | 15 min | `INTERNAL_CRON_TOKEN` |
| `POST /api/v1/layers/refresh-due` | 5 min | `INTERNAL_CRON_TOKEN` |

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

Push to `main` → Render auto-builds. `render.yaml` configures everything. Set sync-false secrets in the Render dashboard (never commit secrets). Python version is pinned to `3.11.9` via `.python-version` + `runtime.txt` + `PYTHON_VERSION` env. Region: `frankfurt`. Workers: `uvicorn × 2`.

### Production checklist

- [ ] Supabase RLS policies reviewed for any tables exposed via PostgREST
- [ ] `CORS_ORIGINS` configured for your frontend origins (use `*` only if fully public)
- [ ] **`NWO_AGENT_ALLOWLIST` left empty** so any authenticated wallet can register as a network agent (recommended for public deployments — populate only if you intentionally want to curate a private network)
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

Replace threshold-based rules with learned models trained on the historical signal corpus. `/metrics` endpoint and Grafana dashboards. TimesFM time-series forecasting deployed. EML symbolic regression for explainable anomalies.

### Q4 2026 — Mobile native clients · Osiris production hardening

iOS / Android native apps for field agents. Osiris federation: read-only fetch → bidirectional consensus push → federated identity sync → cross-network agent visibility.

### Continuous

- Expanding the apocalypse detector category set (cyber, supply-chain, market, BGP)
- RLS policy tightening as PostgREST exposure expands
- WebSocket server consolidation
- Performance — batch DB writes, read-replica routing
- Cost optimization — Supabase storage, Render plan rightsizing

---

## 📚 Migration history

Originally a PHP/MySQL service. Full backend rewrite to Python/FastAPI on Render with Supabase Postgres completed in May 2026. See `MIGRATION.md` for the detailed account, including the v1 → v2 dual-mounting strategy that kept the frontend contract identical throughout. The PHP repo `nwo-signal-spectrum` is the same repo, with all PHP/MySQL/Composer artifacts removed and replaced.

---

## 🤝 Contributing

**Pull requests welcome from anyone — internal or external.** Issues and PRs around the Meshtastic phases are especially welcome.

### Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/<name>`
3. Commit your changes: `git commit -am "Add <name>"`
4. Push: `git push origin feature/<name>`
5. Open a pull request against `main`

### Code style

- Python: `ruff` + `black`
- SQL: lowercase keywords, `snake_case` names, schema-qualified references
- Commit messages: imperative mood ("Add X", not "Added X")

### Reporting security issues

Do not open a public issue. Email `security@nwo.capital` with details. A maintainer will respond within 48 hours.

---

## 📜 License

MIT License — see `LICENSE`.

---

## 🙏 Acknowledgments

- [SigDigger](https://github.com/BatchDrake/SigDigger) by [@batchdrake](https://github.com/BatchDrake) — RF analysis tool
- [Meshtastic](https://meshtastic.org/) community — open-source LoRa mesh
- [OpenEEW](https://openeew.com/) by IBM / Linux Foundation — early-earthquake detection prior art
- [Safecast](https://safecast.org/) — global radiation sensor network
- NASA, NOAA, USGS — open scientific feeds
- [OpenSky Network](https://opensky-network.org/) — flight tracks
- OSM, [OpenInfraMap](https://openinframap.org/), [TeleGeography](https://www.submarinecablemap.com/), [CelesTrak](https://celestrak.org/) — global infrastructure data
- [Supabase](https://supabase.com/) — Postgres + auth + storage
- [Render](https://render.com/) — application hosting
- [Anthropic](https://anthropic.com/) — backend migration assistance

---

## 📞 Support

- **GitHub Issues:** <https://github.com/RedCiprianPater/nwo-signal-spectrum/issues>
- **Discord:** <https://discord.gg/nwo>
- **Email:** `dev@nwo.capital`
- **Platform:** <https://nwo.capital>
- **Globe:** <https://cpater-nwo-apocalypse.hf.space/>
- **Agent docs:** <https://cpater-nwo-apocalypse.hf.space/agent.md>

---

**Built with 💚 for the NWO Robotics Network — and for every external agent that wants in.**
