"""Redis (async). Replaces phpredis pub/sub used by handleSignals() to broadcast new signals.

Channels (keep these in sync with whatever your frontend WS subscribes to):
  signals:new        — new signal created
  signals:update     — signal updated / classified
  apocalypse:level   — level changes
  agents:online      — agent join/leave
  consensus:tasks    — new consensus task
  consensus:vote     — vote cast on a task
"""
from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis, from_url

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: Redis | None = None


async def init_redis() -> Redis:
    global _client
    if _client is not None:
        return _client
    settings = get_settings()
    _client = from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
    )
    # Fail-fast on bad URL/credentials.
    await _client.ping()
    logger.info("redis connected")
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("redis closed")


def get_redis() -> Redis:
    if _client is None:
        raise RuntimeError("Redis not initialized — call init_redis() at startup")
    return _client


async def broadcast(channel: str, payload: dict[str, Any]) -> int:
    """Publish a JSON payload on a channel. Returns number of subscribers reached."""
    try:
        return await get_redis().publish(channel, json.dumps(payload, default=str))
    except Exception:
        # Broadcast failures must never break the API request — log and continue.
        logger.exception("redis broadcast failed channel=%s", channel)
        return 0
