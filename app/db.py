"""asyncpg connection pool, wired for Supabase Supavisor (transaction pooler, port 6543).

This version parses the DATABASE_URL manually instead of handing it to asyncpg's
built-in DSN parser. The built-in parser breaks on auto-generated Supabase
passwords that contain `:`, `@`, `[`, `]`, `#`, or other URL-reserved characters
— it can split the URL in the wrong places and attempt to use a chunk of the
password as a port number, hostname, or IPv6 address.

By splitting the URL ourselves (rightmost `@` for auth/host boundary, FIRST `:`
for user/password boundary) and passing keyword arguments to create_pool(),
the password can contain any character without URL-encoding.

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
from urllib.parse import unquote

import asyncpg

from app.config import get_settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


def _parse_pg_url(dsn: str) -> dict:
    """Parse a PostgreSQL connection string robustly.

    Returns kwargs suitable for asyncpg.create_pool().

    Strategy:
      1. Strip scheme (postgres:// or postgresql://)
      2. Strip query string (sslmode etc. — not currently passed through)
      3. Split on the RIGHTMOST `@` — separates auth from host
      4. Split auth on the FIRST `:` — user, then password (which may contain `:`)
      5. Parse host[:port][/database]
    """
    original = dsn

    # 1. Strip scheme
    for scheme in ("postgresql://", "postgres://"):
        if dsn.startswith(scheme):
            dsn = dsn[len(scheme):]
            break
    else:
        raise ValueError(
            f"DATABASE_URL must start with postgresql:// — got: {original[:30]}..."
        )

    # 2. Strip query string
    if "?" in dsn:
        dsn, _query = dsn.split("?", 1)

    # 3. Find rightmost @ — boundary between auth and host
    if "@" not in dsn:
        raise ValueError("DATABASE_URL missing '@' between credentials and host")
    auth, hostpart = dsn.rsplit("@", 1)

    # 4. Split auth on FIRST colon (password may contain more colons)
    if ":" in auth:
        user, password = auth.split(":", 1)
    else:
        user, password = auth, ""

    # 5. Parse host[:port][/database]
    database = "postgres"
    if "/" in hostpart:
        hostport, database = hostpart.split("/", 1)
        # Database might have its own query string fragment
        if "?" in database:
            database, _ = database.split("?", 1)
    else:
        hostport = hostpart

    # Host:port — Supabase pooler is always IPv4 host + port, no brackets
    if ":" in hostport and not hostport.startswith("["):
        host, port_str = hostport.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port in DATABASE_URL: {port_str!r}")
    else:
        host = hostport.strip("[]")
        port = 5432

    return {
        "user": unquote(user),
        "password": unquote(password) if password else None,
        "host": host,
        "port": port,
        "database": database or "postgres",
    }


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Run on every new pooled connection. Sets the schema search path."""
    await conn.execute("SET search_path = spectrum, public")


async def init_pool() -> asyncpg.Pool:
    """Initialize the global pool. Called once at app startup."""
    global _pool
    if _pool is not None:
        return _pool

    settings = get_settings()
    conn_kwargs = _parse_pg_url(settings.database_url)

    # Log host + user + port to help diagnose connection issues.
    # Never log the password.
    logger.info(
        "connecting to postgres: host=%s port=%s user=%s db=%s",
        conn_kwargs["host"],
        conn_kwargs["port"],
        conn_kwargs["user"],
        conn_kwargs["database"],
    )

    _pool = await asyncpg.create_pool(
        **conn_kwargs,
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
