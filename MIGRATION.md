# Migration: PHP → Python (FastAPI on Render + Supabase)

This replaces the entire PHP backend with a Python/FastAPI service. The HTTP
contract is unchanged, so the React frontend on `nwo.capital/asi` keeps working
after you point its `API_BASE` at the new Render service.

## What got migrated

| PHP handler            | Python module                                |
| ---------------------- | -------------------------------------------- |
| `handleAuth()`         | `app/routes/v1/auth.py`                      |
| `handleSignals()`      | `app/routes/v1/signals.py`                   |
| `handleAgents()`       | `app/routes/v1/agents.py`                    |
| `handleNetwork()`      | `app/routes/v1/network.py`                   |
| `handleApocalypse()`   | `app/routes/v1/apocalypse.py` + `services/apocalypse_indicators.py` |
| `handleSpectrum()`     | `app/routes/v1/spectrum.py` + `services/spectrum.py` |
| `handleWsToken()`      | `app/routes/v1/ws_token.py`                  |
| `handleV2Routes()`     | `app/routes/v2/__init__.py` mount in `main.py` |
| `handleV2Apocalypse()` | `app/routes/v2/apocalypse.py` (unified)      |
| `handleHealth()`       | `/health` in `app/main.py`                   |
| Guzzle for Osiris      | `app/services/osiris.py` (httpx async)       |

v2 endpoints `intelligence`, `threats`, `consensus` are in
`app/routes/v2/{intelligence,threats,consensus}.py`.

## Deploy

### 1. Supabase
- Create a Supabase project. Grab the **Transaction Pooler** URI from
  *Project Settings → Database → Connection string → Transaction* — port 6543.
- Open the SQL editor, paste `app/schemas/supabase_schema.sql`, run.

### 2. Redis
- Either Render Key-Value (formerly Render Redis), or Upstash free tier.
- Copy the `rediss://` URI.

### 3. Render
- Push this code as a new repo (or replace the existing PHP repo's contents).
- New Web Service → connect repo → Render reads `render.yaml` and provisions it.
- Set the sync-false secrets in the dashboard:
  `DATABASE_URL`, `REDIS_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`,
  `OSIRIS_API_URL`, `OSIRIS_API_KEY`, `NASA_API_KEY`, `ADSBEXCHANGE_API_KEY`.
- Deploy. `/health` should return `"status": "healthy"`.

### 4. Frontend
- In your React app, update `API_BASE` to the new Render URL (e.g.
  `https://nwo-signal-spectrum.onrender.com`).
- Auth headers stay the same: `X-NWO-Wallet`, `X-NWO-Signature` on POST `/api/v1/auth`,
  then `Authorization: Bearer <token>` on everything else.

### 5. Decommission PHP
- Once the frontend has been running on the Render URL for a release cycle,
  delete `api/`, `composer.json`, `vendor/`, and the Guzzle stuff. The PHP
  router is no longer reachable.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your dev Supabase + Redis
uvicorn app.main:app --reload --port 8080
```

Visit `http://localhost:8080/docs` for the auto-generated OpenAPI UI.

## Why no Guzzle

`httpx` is the standard async HTTP client for Python. The `app/services/osiris.py`
module gives you the same ergonomics Guzzle was providing — a singleton client
with pooled connections, configurable timeouts, retries on transport errors,
and clean async/await. You don't need to vendor anything by hand.

## Why asyncpg, not supabase-py

`supabase-py` wraps PostgREST, which means every query is an HTTP round-trip with
URL-encoded filter syntax. `asyncpg` over the Supavisor pooler gives you direct
SQL — orders of magnitude faster and you can paste your existing PHP queries in
with minor PostgreSQL syntax fixes. The `SUPABASE_*` env vars are kept around in
case you want to mix in PostgREST or the JS client for the frontend.

## Notes & footguns

- **Supavisor transaction pooler doesn't support prepared statements.** This is
  why `app/db.py` sets `statement_cache_size=0`. Without that, queries fail
  intermittently with a confusing "prepared statement already exists" error.
- **CORS**: set `CORS_ORIGINS` to a comma-separated list of every origin you
  want (e.g. `https://nwo.capital,http://localhost:5173`).
- **Free Render web services sleep after 15 min idle.** First request after
  sleep takes ~30s. If that matters for `apocalypse:check` cron, upgrade to
  the Starter plan ($7/mo) or use a separate scheduler.
- **WebSocket layer**: this service issues short-lived WS tokens
  (`POST /api/v1/ws-token`) but doesn't itself accept WS connections — the
  intent is a separate WS-server process that validates tokens against the
  same Redis. If you want WS in the same FastAPI process, add a route with
  `@app.websocket("/stream")` and validate the token query param against
  Redis key `ws_token:<token>`.
