"""Spectrum analysis service.

This is a thin Python-side abstraction over the existing spectrum-monitor.py
work. The web service doesn't itself run SDR — it queries the results that
spectrum-monitor.py (or any other producer) writes to the DB.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import asyncpg


# Standard frequency band labels used in /spectrum/frequency-bands
FREQUENCY_BANDS: list[dict[str, Any]] = [
    {"name": "LF",  "min_hz":        30_000, "max_hz":       300_000},
    {"name": "MF",  "min_hz":       300_000, "max_hz":     3_000_000},
    {"name": "HF",  "min_hz":     3_000_000, "max_hz":    30_000_000},
    {"name": "VHF", "min_hz":    30_000_000, "max_hz":   300_000_000},
    {"name": "UHF", "min_hz":   300_000_000, "max_hz": 3_000_000_000},
    {"name": "SHF", "min_hz": 3_000_000_000, "max_hz": 30_000_000_000},
]


def band_for(freq_hz: int) -> str | None:
    for b in FREQUENCY_BANDS:
        if b["min_hz"] <= freq_hz < b["max_hz"]:
            return b["name"]
    return None


async def analyze(conn: asyncpg.Connection, signal_id: int) -> dict[str, Any]:
    """Return analysis data for a stored signal (used by /spectrum/analyze)."""
    row = await conn.fetchrow(
        """
        SELECT id, frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
               classification, latitude, longitude, metadata, created_at
        FROM signals
        WHERE id = $1
        """,
        signal_id,
    )
    if row is None:
        return {}
    data = dict(row)
    data["band"] = band_for(int(data["frequency_hz"]))
    data["analyzed_at"] = datetime.now(timezone.utc)
    return data


async def share(conn: asyncpg.Connection, signal_id: int, share_token: str) -> bool:
    await conn.execute(
        """
        INSERT INTO signal_shares (signal_id, share_token, created_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (share_token) DO NOTHING
        """,
        signal_id,
        share_token,
    )
    return True
