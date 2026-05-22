"""Reusable FastAPI dependencies."""
from __future__ import annotations

from typing import Annotated, AsyncIterator

import asyncpg
from fastapi import Depends, Header, HTTPException, status

from app.auth import Session, resolve_session
from app.db import acquire


async def db_conn() -> AsyncIterator[asyncpg.Connection]:
    async with acquire() as conn:
        yield conn


DbConn = Annotated[asyncpg.Connection, Depends(db_conn)]


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
