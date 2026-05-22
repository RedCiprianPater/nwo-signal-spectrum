"""Pydantic models for request bodies and response payloads."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Auth ----------

class AuthRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2048)
    timestamp: int
    nonce: str | None = None


class AuthResponse(BaseModel):
    wallet: str
    token: str
    expires_at: int


# ---------- Signals ----------

class SignalLocation(BaseModel):
    lat: float | None = None
    lon: float | None = None


class SignalCreate(BaseModel):
    frequency_hz: int = Field(..., ge=0)
    bandwidth_hz: int = Field(..., ge=0)
    modulation: str | None = None
    signal_strength_dbm: float | None = None
    classification: str = "unknown"
    location: SignalLocation | None = None
    metadata: dict[str, Any] | None = None


class SignalUpdate(BaseModel):
    modulation: str | None = None
    signal_strength_dbm: float | None = None
    classification: str | None = None
    metadata: dict[str, Any] | None = None


class SignalRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    frequency_hz: int
    bandwidth_hz: int
    modulation: str | None
    signal_strength_dbm: float | None
    classification: str
    latitude: float | None = None
    longitude: float | None = None
    submitter_wallet: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime


# ---------- Agents ----------

class AgentRegister(BaseModel):
    capabilities: list[str] = Field(default_factory=list)
    region: str | None = None


class AgentRecord(BaseModel):
    id: int
    wallet: str
    capabilities: list[str]
    region: str | None
    last_seen: datetime
    online: bool


# ---------- Consensus / Network ----------

class TaskSubmit(BaseModel):
    type: str
    signal_id: int | None = None
    proposed_class: str | None = None
    evidence: list[str] = Field(default_factory=list)
    payload: dict[str, Any] | None = None


class VoteSubmit(BaseModel):
    task_id: int
    classification: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = None


# ---------- Apocalypse ----------

ApocalypseSeverity = Literal["low", "medium", "high", "critical", "extreme"]


class ApocalypseLevel(BaseModel):
    level: int = Field(..., ge=1, le=5)
    description: str
    active_signals: int
    breakdown: dict[str, int]
    timestamp: datetime


class ApocalypseAlert(BaseModel):
    id: int
    type: str
    severity: ApocalypseSeverity
    description: str
    region: str | None
    latitude: float | None
    longitude: float | None
    metadata: dict[str, Any] | None
    created_at: datetime


# ---------- v2 ----------

class UnifiedThreat(BaseModel):
    """v2/apocalypse/unified — Osiris + Spectrum combined."""
    unified_level: int
    osiris_level: int | None
    spectrum_level: int
    breakdown: dict[str, Any]
    sources: list[str]
    timestamp: datetime
