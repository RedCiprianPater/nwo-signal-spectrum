"""asyncpg connection pool, wired for Supabase Supavisor (transaction pooler, port 6543).

Two important Supavisor-specific settings:
  - statement_cache_size=0   — transaction pooling can't reuse prepared statements
                               across connections; setting this to 0 prevents
                               "prepared statement does not exist" errors.
  - init=_init_connection    — sets `search_path = spectrum, public` so unqualified
                               table names in route handlers resolve to spectrum.*
                               while cross-schema FKs into public.identities still work.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Run on every new pooled connection. Sets the schema search path."""
    await conn.execute("SET search_path = spectrum, public")


async def init_pool() -> asyncpg.Pool:
    """Initialize the global pool. Called once at app startup."""
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=10,
        command_timeout=30,
        statement_cache_size=0,
        max_inactive_connection_lifetime=300,
        init=_init_connection,
    )
    logger.info("asyncpg pool ready (Supabase pooler, search_path=spectrum,public)")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("asyncpg pool closed")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized — call init_pool() at startup")
    return _pool


@asynccontextmanager
async def acquire() -> AsyncIterator[asyncpg.Connection]:
    """Yield a connection from the pool. Use this inside route handlers."""
    pool = get_pool()
    async with pool.acquire() as conn:
        yield conn
