"""Reusable FastAPI dependencies.

v2.1 change:
    Added `require_session_or_cron` + `AuthSessionOrCron` so the three
    Render cron services can call their internal endpoints with a shared
    bearer token instead of a real user session. Fixes the 15-min
    "invalid or expired session" 401 loop on:

        POST /api/v1/apocalypse/check
        POST /api/v1/layers/refresh-due
        POST /api/v1/layers/bootstrap-country

The existing `require_session` / `AuthSession` are unchanged, so every
other endpoint in the tree behaves identically. Existing sessions and
API keys keep working as before.
"""
from __future__ import annotations

import hmac
import os
import time
from typing import Annotated, AsyncIterator

import asyncpg
from fastapi import Depends, Header, HTTPException, status

from app.auth import Session, resolve_session
from app.db import acquire


# ============================================================
# Database
# ============================================================

async def db_conn() -> AsyncIterator[asyncpg.Connection]:
    async with acquire() as conn:
        yield conn


DbConn = Annotated[asyncpg.Connection, Depends(db_conn)]


# ============================================================
# Session auth — user path (unchanged from v2.0)
# ============================================================

async def require_session(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Session:
    """Reject the request unless a valid Bearer session token is present."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    session = await resolve_session(token)
    if session is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


AuthSession = Annotated[Session, Depends(require_session)]


# ============================================================
# Cron auth  (v2.1 — for INTERNAL_CRON_TOKEN endpoints)
# ============================================================
#
# The three endpoints wired to Render cron services must be callable
# without a user session:
#
#     POST /api/v1/apocalypse/check          — every 15 min
#     POST /api/v1/layers/refresh-due        — every 5 min
#     POST /api/v1/layers/bootstrap-country  — daily 03:30 UTC
#
# The cron services send:
#
#     Authorization: Bearer <INTERNAL_CRON_TOKEN>
#
# If the bearer matches the value in the environment we synthesize a
# sentinel Session so downstream endpoint code (which only checks that
# a Session exists, never its wallet/identity contents) keeps working.
#
# When the bearer does NOT match the cron token we fall back to the
# normal Redis session lookup — so a human with a valid session can
# still trigger a manual /check from the dashboard.
#
# IMPORTANT: INTERNAL_CRON_TOKEN must be set to the IDENTICAL string
# on the web service AND on every cron service in Render. Both are
# `sync: false` in render.yaml, so Render treats them as independent
# secrets; if the values drift, this endpoint 401s again.
# ============================================================

# Deterministic sentinel identifiers for the cron "user".
# All-zeros EVM address (nobody controls it) and the RFC-4122 nil UUID.
# Both are safe to place in a frozen Session dataclass.
_CRON_WALLET = "0x0000000000000000000000000000000000000000"
_CRON_IDENTITY_ID = "00000000-0000-0000-0000-000000000000"


def _cron_token_matches(candidate: str) -> bool:
    """Constant-time compare of the presented bearer against INTERNAL_CRON_TOKEN.

    Returns False when the env var is unset, empty, or does not match — never
    raises. This lets the endpoint silently disable the cron path in dev
    environments where INTERNAL_CRON_TOKEN was never configured.
    """
    expected = os.environ.get("INTERNAL_CRON_TOKEN", "")
    if not expected or not candidate:
        return False
    return hmac.compare_digest(expected, candidate)


async def require_session_or_cron(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Session:
    """Accept EITHER a valid user session OR the shared INTERNAL_CRON_TOKEN.

    Order of checks:
        1. Bearer header present?               → 401 if missing.
        2. Bearer value == INTERNAL_CRON_TOKEN? → synthesize a cron Session.
        3. Bearer value is a live Redis session? → return that real Session.
        4. Otherwise                            → 401 "invalid or expired session".

    Endpoints always receive a Session on success, so their signatures
    do not need to change to opt into cron access — they just annotate
    the parameter as AuthSessionOrCron instead of AuthSession.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()

    # Fast path — internal cron token. Constant-time compare, no Redis hit.
    if _cron_token_matches(token):
        return Session(
            wallet=_CRON_WALLET,
            identity_id=_CRON_IDENTITY_ID,
            issued_at=int(time.time()),
        )

    # Normal user session lookup.
    session = await resolve_session(token)
    if session is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


AuthSessionOrCron = Annotated[Session, Depends(require_session_or_cron)]
