"""FastAPI app entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8080

On Render:
    See render.yaml — `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
"""
from __future__ import annotations

import logging
import logging.config
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import close_pool, init_pool
from app.redis_client import close_redis, init_redis
from app.routes.v1 import agents as v1_agents
from app.routes.v1 import apocalypse as v1_apocalypse
from app.routes.v1 import auth as v1_auth
from app.routes.v1 import network as v1_network
from app.routes.v1 import signals as v1_signals
from app.routes.v1 import spectrum as v1_spectrum
from app.routes.v1 import ws_token as v1_ws
from app.routes.v2 import apocalypse as v2_apocalypse
from app.routes.v2 import consensus as v2_consensus
from app.routes.v2 import intelligence as v2_intelligence
from app.routes.v2 import threats as v2_threats
from app.services import osiris


def _configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown: build the pools, then tear them down cleanly."""
    _configure_logging()
    await init_pool()
    await init_redis()
    await osiris.init_osiris()
    try:
        yield
    finally:
        await osiris.close_osiris()
        await close_redis()
        await close_pool()


settings = get_settings()

app = FastAPI(
    title="NWO Signal Spectrum API",
    description="Multi-Agent RF Signal Analysis & Apocalypse Detection Network",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-Id"],
)


# ----- Health & version -----

@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Liveness + version. Used by Render healthCheckPath and uptime monitors."""
    from app.db import get_pool
    from app.redis_client import get_redis

    db_ok = True
    redis_ok = True
    try:
        async with get_pool().acquire() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_ok = False
    try:
        await get_redis().ping()
    except Exception:
        redis_ok = False

    return {
        "status": "healthy" if db_ok and redis_ok else "degraded",
        "version": settings.app_version,
        "api_versions": ["v1", "v2"],
        "services": {
            "database": "up" if db_ok else "down",
            "redis": "up" if redis_ok else "down",
        },
        "timestamp": int(time.time()),
    }


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("app").exception("unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


# ----- v1 mount -----

V1 = "/api/v1"
app.include_router(v1_auth.router,        prefix=V1)
app.include_router(v1_signals.router,     prefix=V1)
app.include_router(v1_agents.router,      prefix=V1)
app.include_router(v1_network.router,     prefix=V1)
app.include_router(v1_apocalypse.router,  prefix=V1)
app.include_router(v1_spectrum.router,    prefix=V1)
app.include_router(v1_ws.router,          prefix=V1)

# ----- v2 mount -----

V2 = "/api/v2"
app.include_router(v2_intelligence.router, prefix=V2)
app.include_router(v2_threats.router,      prefix=V2)
app.include_router(v2_consensus.router,    prefix=V2)
app.include_router(v2_apocalypse.router,   prefix=V2)
