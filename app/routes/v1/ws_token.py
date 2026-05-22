"""/api/v1/ws-token — short-lived token for WebSocket auth.

The frontend hits this *after* having an HTTP session, gets a one-shot token
with ~60s expiry, then opens a WS to ws://.../stream?token=<...>. The WS
server validates the token against the same Redis store.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.deps import AuthSession
from app.redis_client import get_redis

router = APIRouter(prefix="/ws-token", tags=["ws"])

WS_TOKEN_TTL_SECONDS = 60
WS_TOKEN_PREFIX = "ws_token:"


@router.post("", status_code=status.HTTP_201_CREATED)
async def issue_ws_token(session: AuthSession) -> dict:
    token = secrets.token_urlsafe(24)
    await get_redis().setex(
        f"{WS_TOKEN_PREFIX}{token}", WS_TOKEN_TTL_SECONDS, session.wallet
    )
    ws_base = os.environ.get("WS_BASE_URL", "wss://signal.nwo.capital/stream")
    return {
        "token": token,
        "ws_url": f"{ws_base}?token={token}",
        "expires_at": int(datetime.now(timezone.utc).timestamp()) + WS_TOKEN_TTL_SECONDS,
    }
