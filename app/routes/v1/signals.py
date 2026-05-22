"""/api/v1/signals — GET/POST/PUT signals + Redis broadcast.

Direct port of the PHP handleSignals(). Behaviour matches what the React
frontend expects: list with filters, single fetch, create, update.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.deps import AuthSession, DbConn
from app.models import SignalCreate, SignalRecord, SignalUpdate
from app.redis_client import broadcast

router = APIRouter(prefix="/signals", tags=["signals"])


def _row_to_record(r) -> dict[str, Any]:
    d = dict(r)
    if d.get("metadata") and isinstance(d["metadata"], str):
        d["metadata"] = json.loads(d["metadata"])
    return d


@router.get("", response_model=list[SignalRecord])
async def list_signals(
    conn: DbConn,
    session: AuthSession,
    freq_min: int | None = Query(None, ge=0),
    freq_max: int | None = Query(None, ge=0),
    classification: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[SignalRecord]:
    clauses = []
    params: list[Any] = []
    if freq_min is not None:
        params.append(freq_min)
        clauses.append(f"frequency_hz >= ${len(params)}")
    if freq_max is not None:
        params.append(freq_max)
        clauses.append(f"frequency_hz <= ${len(params)}")
    if classification:
        params.append(classification)
        clauses.append(f"classification = ${len(params)}")
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    params.extend([limit, offset])
    rows = await conn.fetch(
        f"""
        SELECT id, frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
               classification, latitude, longitude, submitter_wallet, metadata, created_at
        FROM signals
        {where}
        ORDER BY created_at DESC
        LIMIT ${len(params) - 1} OFFSET ${len(params)}
        """,
        *params,
    )
    return [SignalRecord(**_row_to_record(r)) for r in rows]


@router.get("/{signal_id}", response_model=SignalRecord)
async def get_signal(signal_id: int, conn: DbConn, session: AuthSession) -> SignalRecord:
    row = await conn.fetchrow(
        """
        SELECT id, frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
               classification, latitude, longitude, submitter_wallet, metadata, created_at
        FROM signals WHERE id = $1
        """,
        signal_id,
    )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="signal not found")
    return SignalRecord(**_row_to_record(row))


@router.post("", response_model=SignalRecord, status_code=status.HTTP_201_CREATED)
async def create_signal(
    body: SignalCreate, conn: DbConn, session: AuthSession
) -> SignalRecord:
    lat = body.location.lat if body.location else None
    lon = body.location.lon if body.location else None
    row = await conn.fetchrow(
        """
        INSERT INTO signals (
            frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
            classification, latitude, longitude, submitter_wallet, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        RETURNING id, frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
                  classification, latitude, longitude, submitter_wallet, metadata, created_at
        """,
        body.frequency_hz,
        body.bandwidth_hz,
        body.modulation,
        body.signal_strength_dbm,
        body.classification,
        lat,
        lon,
        session.wallet,
        json.dumps(body.metadata or {}),
    )
    record = SignalRecord(**_row_to_record(row))

    await broadcast("signals:new", record.model_dump(mode="json"))
    return record


@router.put("/{signal_id}", response_model=SignalRecord)
async def update_signal(
    signal_id: int, body: SignalUpdate, conn: DbConn, session: AuthSession
) -> SignalRecord:
    # Build a dynamic UPDATE — only set fields that were provided.
    updates: list[str] = []
    params: list[Any] = []
    for field in ("modulation", "signal_strength_dbm", "classification"):
        val = getattr(body, field)
        if val is not None:
            params.append(val)
            updates.append(f"{field} = ${len(params)}")
    if body.metadata is not None:
        params.append(json.dumps(body.metadata))
        updates.append(f"metadata = ${len(params)}::jsonb")
    if not updates:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="no fields to update")

    params.append(signal_id)
    row = await conn.fetchrow(
        f"""
        UPDATE signals SET {", ".join(updates)}
        WHERE id = ${len(params)}
        RETURNING id, frequency_hz, bandwidth_hz, modulation, signal_strength_dbm,
                  classification, latitude, longitude, submitter_wallet, metadata, created_at
        """,
        *params,
    )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="signal not found")
    record = SignalRecord(**_row_to_record(row))

    await broadcast("signals:update", record.model_dump(mode="json"))
    return record
