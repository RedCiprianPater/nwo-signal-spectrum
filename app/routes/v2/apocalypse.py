"""/api/v2/apocalypse/unified — the headline v2 endpoint.

Combines:
  - Local spectrum-driven level (from apocalypse_indicators.current_level)
  - Osiris global threat level
into a single unified level. Falls back gracefully if Osiris is unreachable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

from app.deps import AuthSession, DbConn
from app.models import UnifiedThreat
from app.services import apocalypse_indicators as indicators
from app.services import osiris

router = APIRouter(prefix="/apocalypse", tags=["v2:apocalypse"])


@router.get("/unified", response_model=UnifiedThreat)
async def unified(conn: DbConn, session: AuthSession) -> UnifiedThreat:
    spectrum = await indicators.current_level(conn)
    osiris_data = await osiris.fetch_threat_level()

    spectrum_level = int(spectrum["level"])
    osiris_level: int | None = None
    sources = ["spectrum"]

    if osiris_data and isinstance(osiris_data, dict):
        try:
            osiris_level = int(osiris_data.get("level", 0))
            sources.append("osiris")
        except (TypeError, ValueError):
            osiris_level = None

    # Unified = max of the two (worst-case wins), capped at 5.
    unified_level = max(spectrum_level, osiris_level or 0)

    return UnifiedThreat(
        unified_level=unified_level,
        osiris_level=osiris_level,
        spectrum_level=spectrum_level,
        breakdown={
            "spectrum": spectrum["breakdown"],
            "osiris": osiris_data or {},
        },
        sources=sources,
        timestamp=datetime.now(timezone.utc),
    )
