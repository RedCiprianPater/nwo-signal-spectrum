"""Osiris API client.

This is the direct replacement for the Guzzle-based PHP service. httpx gives us:
  - Async by default (composes with FastAPI)
  - Connection pooling via a singleton client
  - Same retry / timeout ergonomics as Guzzle, less ceremony

The Osiris service is the upstream provider of the *external* threat-intelligence
half of /api/v2/apocalypse/unified. We never let an Osiris outage 500 our endpoint
— if it's down we return null in the Osiris fields and the unified level falls
back to the spectrum-only calculation.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def _build_client() -> httpx.AsyncClient:
    settings = get_settings()
    headers: dict[str, str] = {"Accept": "application/json", "User-Agent": "nwo-spectrum/2.0"}
    if settings.osiris_api_key:
        headers["Authorization"] = f"Bearer {settings.osiris_api_key}"
    return httpx.AsyncClient(
        base_url=settings.osiris_api_url,
        headers=headers,
        timeout=httpx.Timeout(settings.osiris_timeout_seconds),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    )


async def init_osiris() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = _build_client()
    return _client


async def close_osiris() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _client_or_raise() -> httpx.AsyncClient:
    if _client is None:
        raise RuntimeError("Osiris client not initialized")
    return _client


async def fetch_threat_level() -> dict[str, Any] | None:
    """GET /threat-level on Osiris. Returns None on failure so callers can degrade gracefully."""
    try:
        r = await _client_or_raise().get("/threat-level")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        logger.warning("osiris threat-level fetch failed: %s", exc)
        return None


async def fetch_intelligence(category: str | None = None) -> list[dict[str, Any]]:
    """GET /intelligence — feed for v2/intelligence."""
    params = {"category": category} if category else None
    try:
        r = await _client_or_raise().get("/intelligence", params=params)
        r.raise_for_status()
        data = r.json()
        return data.get("items", []) if isinstance(data, dict) else data
    except httpx.HTTPError as exc:
        logger.warning("osiris intelligence fetch failed: %s", exc)
        return []


async def fetch_threats(severity: str | None = None, hours: int = 24) -> list[dict[str, Any]]:
    """GET /threats — feed for v2/threats."""
    params: dict[str, Any] = {"hours": hours}
    if severity:
        params["severity"] = severity
    try:
        r = await _client_or_raise().get("/threats", params=params)
        r.raise_for_status()
        data = r.json()
        return data.get("items", []) if isinstance(data, dict) else data
    except httpx.HTTPError as exc:
        logger.warning("osiris threats fetch failed: %s", exc)
        return []


async def post_consensus(payload: dict[str, Any]) -> dict[str, Any] | None:
    """POST consensus result back to Osiris for cross-network aggregation."""
    try:
        r = await _client_or_raise().post("/consensus", json=payload)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        logger.warning("osiris consensus post failed: %s", exc)
        return None
