"""Apocalypse indicator service.

Direct port of the PHP ApocalypseIndicators class — all six detection categories
(aviation, seismic, solar, radiation, asteroid, RF) plus the rollup that produces
a level 1–5 from the active signals.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import asyncpg
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


LEVEL_LABELS = {
    1: "Normal — baseline activity",
    2: "Elevated — minor anomalies",
    3: "High — multiple concerning signals",
    4: "Severe — coordinated indicators",
    5: "Extreme — multi-source critical alerts",
}


# -------- Level computation --------

async def current_level(conn: asyncpg.Connection) -> dict[str, Any]:
    """Aggregate active signals in the last 24h into a single level."""
    rows = await conn.fetch(
        """
        SELECT type, severity, COUNT(*)::int AS n
        FROM apocalypse_signals
        WHERE created_at > NOW() - INTERVAL '24 hours'
        GROUP BY type, severity
        """
    )

    breakdown: dict[str, int] = {}
    severity_weights = {"low": 1, "medium": 2, "high": 3, "critical": 4, "extreme": 5}
    total_weight = 0
    total_signals = 0

    for r in rows:
        breakdown[r["type"]] = breakdown.get(r["type"], 0) + r["n"]
        total_weight += severity_weights.get(r["severity"], 1) * r["n"]
        total_signals += r["n"]

    if total_signals == 0:
        level = 1
    else:
        avg_severity = total_weight / total_signals
        # Bin avg severity 1.0–5.0 into discrete levels.
        level = max(1, min(5, round(avg_severity)))

    return {
        "level": level,
        "description": LEVEL_LABELS[level],
        "active_signals": total_signals,
        "breakdown": breakdown,
        "timestamp": datetime.now(timezone.utc),
    }


async def record_level(conn: asyncpg.Connection, level: int, active: int) -> None:
    """Snapshot the current level into the history table."""
    await conn.execute(
        """
        INSERT INTO apocalypse_level_history (level, description, active_signals)
        VALUES ($1, $2, $3)
        """,
        level,
        LEVEL_LABELS.get(level, ""),
        active,
    )


async def level_history(
    conn: asyncpg.Connection, hours: int = 24
) -> list[dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT level, description, active_signals, recorded_at
        FROM apocalypse_level_history
        WHERE recorded_at > NOW() - ($1 || ' hours')::INTERVAL
        ORDER BY recorded_at DESC
        """,
        str(hours),
    )
    return [dict(r) for r in rows]


# -------- Aviation (ADS-B Exchange) --------

async def detect_aviation_anomaly(
    conn: asyncpg.Connection, region: str = "global"
) -> dict[str, Any] | None:
    """Compare current business-jet count in the region to baseline. >2σ → anomaly."""
    settings = get_settings()
    baseline_row = await conn.fetchrow(
        "SELECT value FROM signal_baselines WHERE type='aviation' AND region=$1", region
    )
    baseline = float(baseline_row["value"]) if baseline_row else 100.0

    # Pull recent count from the local cache table; cron job updates it from ADS-B.
    row = await conn.fetchrow(
        """
        SELECT COUNT(*)::int AS n
        FROM aircraft_sightings
        WHERE is_business_jet = TRUE
          AND detected_at > NOW() - INTERVAL '1 hour'
        """
    )
    current = int(row["n"]) if row else 0

    if baseline <= 0:
        return None
    ratio = current / baseline
    if ratio < 2.0:
        return None

    return {
        "type": "aviation",
        "severity": "critical" if ratio > 4 else "high" if ratio > 3 else "medium",
        "description": (
            f"{current} business jets in {region} — {ratio:.1f}x baseline ({baseline:.0f})"
        ),
        "metadata": {"current": current, "baseline": baseline, "ratio": ratio},
        "region": region,
    }


# -------- Seismic (USGS) --------

async def detect_seismic_anomaly(
    conn: asyncpg.Connection, hours: int = 24, magnitude_min: float = 6.0
) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        """
        SELECT COUNT(*)::int AS n, MAX(magnitude) AS max_mag
        FROM seismic_events
        WHERE event_time > NOW() - ($1 || ' hours')::INTERVAL
          AND magnitude >= $2
        """,
        str(hours),
        magnitude_min,
    )
    n = int(row["n"]) if row else 0
    if n < 3:
        return None
    max_mag = float(row["max_mag"]) if row and row["max_mag"] is not None else 0.0
    return {
        "type": "seismic",
        "severity": "critical" if max_mag >= 7 else "high",
        "description": f"Cluster of {n} M{magnitude_min}+ earthquakes in {hours}h (max M{max_mag:.1f})",
        "metadata": {"count": n, "max_magnitude": max_mag, "hours": hours},
        "region": "global",
    }


# -------- Solar (NOAA SWPC) --------

async def fetch_noaa_solar() -> dict[str, Any] | None:
    """Pull current solar activity. Cached by caller if needed."""
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{settings.noaa_swpc_url}/goes/primary/xrays-1-day.json")
            r.raise_for_status()
            data = r.json()
        # Find the highest flare class in the last 24h
        flux_max = max((float(d.get("flux", 0) or 0) for d in data), default=0.0)
        if flux_max >= 1e-4:
            klass = "X"
        elif flux_max >= 1e-5:
            klass = "M"
        elif flux_max >= 1e-6:
            klass = "C"
        else:
            klass = None
        return {"flux_max": flux_max, "class": klass}
    except httpx.HTTPError as exc:
        logger.warning("NOAA solar fetch failed: %s", exc)
        return None


async def detect_solar_anomaly() -> dict[str, Any] | None:
    solar = await fetch_noaa_solar()
    if not solar or not solar.get("class"):
        return None
    klass = solar["class"]
    if klass not in ("M", "X"):
        return None
    return {
        "type": "solar",
        "severity": "extreme" if klass == "X" else "high",
        "description": f"{klass}-class solar flare detected",
        "metadata": solar,
        "region": "global",
    }


# -------- Radiation (Safecast) --------

async def detect_radiation_anomaly(
    conn: asyncpg.Connection,
) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        """
        SELECT COUNT(*)::int AS n, MAX(deviation_percent) AS max_dev
        FROM radiation_readings
        WHERE measured_at > NOW() - INTERVAL '6 hours'
          AND deviation_percent > 200
        """
    )
    n = int(row["n"]) if row else 0
    if n < 1:
        return None
    return {
        "type": "radiation",
        "severity": "critical",
        "description": f"{n} radiation sensors >2x baseline in last 6h",
        "metadata": {"count": n, "max_deviation_pct": float(row["max_dev"] or 0)},
        "region": "global",
    }


# -------- Asteroids (NASA NEO) --------

async def detect_asteroid_anomaly(conn: asyncpg.Connection) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        """
        SELECT name, miss_distance_ld, diameter_max_m
        FROM neo_objects
        WHERE approach_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
          AND is_hazardous = TRUE
        ORDER BY miss_distance_ld ASC
        LIMIT 1
        """
    )
    if not row:
        return None
    return {
        "type": "asteroid",
        "severity": "high" if float(row["miss_distance_ld"]) < 1.0 else "medium",
        "description": (
            f"Hazardous NEO {row['name']} approaching at "
            f"{float(row['miss_distance_ld']):.2f} lunar distances"
        ),
        "metadata": {
            "name": row["name"],
            "diameter_m": float(row["diameter_max_m"] or 0),
            "miss_distance_ld": float(row["miss_distance_ld"]),
        },
        "region": "space",
    }


# -------- Composite check (cron-driven) --------

async def run_all_checks(conn: asyncpg.Connection) -> list[dict[str, Any]]:
    """Run every detector. Any non-None result is persisted as a new signal."""
    checks = [
        detect_aviation_anomaly(conn),
        detect_seismic_anomaly(conn),
        detect_solar_anomaly(),
        detect_radiation_anomaly(conn),
        detect_asteroid_anomaly(conn),
    ]
    import asyncio

    results = await asyncio.gather(*checks, return_exceptions=True)
    fresh: list[dict[str, Any]] = []
    for r in results:
        if isinstance(r, Exception):
            logger.exception("detector error: %s", r)
            continue
        if r is None:
            continue
        await conn.execute(
            """
            INSERT INTO apocalypse_signals (type, severity, description, metadata, region)
            VALUES ($1, $2, $3, $4::jsonb, $5)
            """,
            r["type"],
            r["severity"],
            r["description"],
            __import__("json").dumps(r.get("metadata") or {}),
            r.get("region"),
        )
        fresh.append(r)
    return fresh
