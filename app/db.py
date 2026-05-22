"""asyncpg connection pool, wired for Supabase Supavisor (transaction pooler, port 6543).

Why asyncpg and not supabase-py? asyncpg gives us:
  - Direct SQL (mirrors what the PHP handlers were doing)
  - Server-side prepared statements (must be disabled for transaction pooling — see below)
  - Significantly lower latency than the PostgREST REST round-trip
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    """Initialize the global pool. Called once at app startup."""
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    # Supavisor transaction pooler does NOT support prepared statements.
    # Setting statement_cache_size=0 is required, otherwise queries fail at random.
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=10,
        command_timeout=30,
        statement_cache_size=0,
        max_inactive_connection_lifetime=300,
    )
    logger.info("asyncpg pool ready (Supabase pooler)")
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
