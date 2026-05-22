"""/api/v1/apocalypse — threat level, alerts, checks, per-category endpoints.

Direct port of handleApocalypse(). All 12 cases from the PHP handler are here:
  level, alerts, check, aviation, seismic, solar, radiation, asteroid, history,
  plus the dashboard summary (default).
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Query

from app.deps import AuthSession, DbConn
from app.models import ApocalypseAlert, ApocalypseLevel
from app.redis_client import broadcast
from app.services import apocalypse_indicators as indicators

router = APIRouter(prefix="/apocalypse", tags=["apocalypse"])


# ----- /level -----

@router.get("/level", response_model=ApocalypseLevel)
async def get_level(conn: DbConn, session: AuthSession) -> ApocalypseLevel:
    level = await indicators.current_level(conn)
    return ApocalypseLevel(**level)


# ----- /alerts -----

@router.get("/alerts", response_model=list[ApocalypseAlert])
async def list_alerts(
    conn: DbConn,
    session: AuthSession,
    severity: str | None = None,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=500),
) -> list[ApocalypseAlert]:
    clauses = [f"created_at > NOW() - ($1 || ' hours')::INTERVAL"]
    params: list[Any] = [str(hours)]
    if severity:
        params.append(severity)
        clauses.append(f"severity = ${len(params)}")
    params.append(limit)
    rows = await conn.fetch(
        f"""
        SELECT id, type, severity, description, region, latitude, longitude,
               metadata, created_at
        FROM apocalypse_signals
        WHERE {" AND ".join(clauses)}
        ORDER BY created_at DESC
        LIMIT ${len(params)}
        """,
        *params,
    )
    out = []
    for r in rows:
        d = dict(r)
        if d.get("metadata") and isinstance(d["metadata"], str):
            d["metadata"] = json.loads(d["metadata"])
        out.append(ApocalypseAlert(**d))
    return out


# ----- /check (cron) -----

@router.post("/check")
async def run_checks(conn: DbConn, session: AuthSession) -> dict[str, Any]:
    fresh = await indicators.run_all_checks(conn)
    if fresh:
        await broadcast("apocalypse:level", {"new_signals": len(fresh)})
    return {"detected": len(fresh), "signals": fresh}


# ----- Per-category endpoints -----

@router.get("/aviation")
async def aviation(
    conn: DbConn, session: AuthSession, region: str = "global"
) -> dict[str, Any] | None:
    return await indicators.detect_aviation_anomaly(conn, region)


@router.get("/seismic")
async def seismic(
    conn: DbConn,
    session: AuthSession,
    hours: int = Query(24, ge=1, le=168),
    magnitude_min: float = Query(6.0, ge=0.0, le=10.0),
) -> dict[str, Any] | None:
    return await indicators.detect_seismic_anomaly(conn, hours=hours, magnitude_min=magnitude_min)


@router.get("/solar")
async def solar(session: AuthSession) -> dict[str, Any] | None:
    return await indicators.detect_solar_anomaly()


@router.get("/radiation")
async def radiation(conn: DbConn, session: AuthSession) -> dict[str, Any] | None:
    return await indicators.detect_radiation_anomaly(conn)


@router.get("/asteroid")
async def asteroid(conn: DbConn, session: AuthSession) -> dict[str, Any] | None:
    return await indicators.detect_asteroid_anomaly(conn)


# ----- /history -----

@router.get("/history")
async def history(
    conn: DbConn, session: AuthSession, hours: int = Query(24, ge=1, le=720)
) -> list[dict[str, Any]]:
    return await indicators.level_history(conn, hours=hours)


# ----- default dashboard -----

@router.get("")
async def dashboard(conn: DbConn, session: AuthSession) -> dict[str, Any]:
    row = await conn.fetchrow(
        "SELECT * FROM apocalypse_dashboard"
    )
    level = await indicators.current_level(conn)
    return {
        "current_level": level,
        "summary": dict(row) if row else {},
    }
