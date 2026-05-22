"""/api/v2/intelligence — combined intelligence feed from Osiris + local signals."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.deps import AuthSession, DbConn
from app.services import osiris

router = APIRouter(prefix="/intelligence", tags=["v2:intelligence"])


@router.get("")
async def get_intelligence(
    conn: DbConn,
    session: AuthSession,
    category: str | None = None,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    # External feed
    osiris_items = await osiris.fetch_intelligence(category=category)

    # Local feed (apocalypse signals tagged as intel-relevant)
    local_rows = await conn.fetch(
        """
        SELECT id, type, severity, description, region, metadata, created_at
        FROM apocalypse_signals
        WHERE created_at > NOW() - ($1 || ' hours')::INTERVAL
          AND ($2::text IS NULL OR type = $2)
        ORDER BY created_at DESC
        LIMIT $3
        """,
        str(hours),
        category,
        limit,
    )

    return {
        "osiris": osiris_items,
        "local": [dict(r) for r in local_rows],
        "category": category,
        "hours": hours,
    }
