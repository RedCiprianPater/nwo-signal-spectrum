"""/api/v2/threats — current threat picture pulled from Osiris and the local DB."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.deps import AuthSession, DbConn
from app.services import osiris

router = APIRouter(prefix="/threats", tags=["v2:threats"])


@router.get("")
async def get_threats(
    conn: DbConn,
    session: AuthSession,
    severity: str | None = Query(None),
    hours: int = Query(24, ge=1, le=168),
) -> dict[str, Any]:
    osiris_threats = await osiris.fetch_threats(severity=severity, hours=hours)

    clauses = [f"created_at > NOW() - ($1 || ' hours')::INTERVAL"]
    params: list[Any] = [str(hours)]
    if severity:
        params.append(severity)
        clauses.append(f"severity = ${len(params)}")

    rows = await conn.fetch(
        f"""
        SELECT id, type, severity, description, region, latitude, longitude,
               metadata, created_at
        FROM apocalypse_signals
        WHERE {" AND ".join(clauses)}
        ORDER BY
          CASE severity
            WHEN 'extreme' THEN 1 WHEN 'critical' THEN 2 WHEN 'high' THEN 3
            WHEN 'medium' THEN 4 ELSE 5
          END,
          created_at DESC
        """,
        *params,
    )
    return {
        "osiris_threats": osiris_threats,
        "local_threats": [dict(r) for r in rows],
        "severity_filter": severity,
        "hours": hours,
    }
