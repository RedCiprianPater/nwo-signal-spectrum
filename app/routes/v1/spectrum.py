"""/api/v1/spectrum — analysis helpers over stored signals."""
from __future__ import annotations

import secrets
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.deps import AuthSession, DbConn
from app.services import spectrum as spectrum_service

router = APIRouter(prefix="/spectrum", tags=["spectrum"])


@router.get("/frequency-bands")
async def frequency_bands(session: AuthSession) -> list[dict[str, Any]]:
    return spectrum_service.FREQUENCY_BANDS


@router.get("/analyze/{signal_id}")
async def analyze(signal_id: int, conn: DbConn, session: AuthSession) -> dict[str, Any]:
    data = await spectrum_service.analyze(conn, signal_id)
    if not data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="signal not found")
    return data


@router.post("/share/{signal_id}")
async def share(signal_id: int, conn: DbConn, session: AuthSession) -> dict[str, Any]:
    token = secrets.token_urlsafe(16)
    await spectrum_service.share(conn, signal_id, token)
    return {"signal_id": signal_id, "share_token": token}
