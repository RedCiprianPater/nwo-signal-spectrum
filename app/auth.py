"""Web3 authentication + identity resolution.

Auth flow (changes from v1):
  1. Client signs canonical message with ethers.signMessage()
  2. Server recovers address with eth_account → verified wallet
  3. Server upserts into public.identities via spectrum.find_or_create_identity_for_wallet()
  4. Session token stored in Redis carries BOTH wallet and identity_id (as JSON)
  5. Subsequent requests resolve back to a Session with both fields

This makes signal-spectrum a first-class consumer of the platform's identity
layer instead of a parallel system keyed on raw wallets.
"""
from __future__ import annotations

import json
import logging
import secrets
import time
from dataclasses import dataclass

import asyncpg
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address

from app.config import get_settings
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

SESSION_TTL_SECONDS = 60 * 60  # 1 hour
SESSION_KEY_PREFIX = "session:"


@dataclass(frozen=True)
class Session:
    wallet: str         # checksum-cased EVM address
    identity_id: str    # UUID from public.identities.id
    issued_at: int


def _normalize_address(addr: str) -> str:
    if not addr:
        raise ValueError("empty address")
    return to_checksum_address(addr)


def verify_signature(wallet: str, message: str, signature: str) -> str:
    """Recover address from a personal_sign signature, compare to claimed wallet.

    Returns the recovered (checksum) address on success.
    Raises ValueError on mismatch or malformed input.
    """
    claimed = _normalize_address(wallet)
    encoded = encode_defunct(text=message)
    try:
        recovered = Account.recover_message(encoded, signature=signature)
    except Exception as exc:
        raise ValueError(f"signature recovery failed: {exc}") from exc
    if to_checksum_address(recovered) != claimed:
        raise ValueError("signature does not match claimed wallet")
    return claimed


def validate_timestamp(timestamp: int) -> None:
    settings = get_settings()
    now = int(time.time())
    if abs(now - int(timestamp)) > settings.nwo_auth_timestamp_window:
        raise ValueError("signed timestamp outside allowed window")


def build_canonical_message(nonce: str, timestamp: int) -> str:
    """The exact string the frontend must sign. Keep in sync with the React side."""
    settings = get_settings()
    return (
        f"{settings.nwo_auth_message_prefix}\n"
        f"Domain: {settings.nwo_auth_domain}\n"
        f"Nonce: {nonce}\n"
        f"Timestamp: {timestamp}"
    )


# ----- Identity resolution -----

async def resolve_identity(conn: asyncpg.Connection, wallet: str) -> str:
    """Find-or-create the identity row for this wallet. Returns UUID as string.

    Uses the spectrum.find_or_create_identity_for_wallet() SQL function so the
    lookup-or-insert is atomic at the DB level (no race between two concurrent
    first-signins for the same wallet).
    """
    row = await conn.fetchrow(
        "SELECT spectrum.find_or_create_identity_for_wallet($1) AS id",
        wallet,
    )
    if row is None or row["id"] is None:
        raise RuntimeError("identity upsert returned no id")
    return str(row["id"])


# ----- Session token storage (Redis) -----

async def issue_session(wallet: str, identity_id: str) -> tuple[str, int]:
    """Generate a session token, store {wallet, identity_id} in Redis. Returns (token, expires_at)."""
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    payload = json.dumps({"wallet": _normalize_address(wallet), "identity_id": identity_id})
    await get_redis().setex(f"{SESSION_KEY_PREFIX}{token}", SESSION_TTL_SECONDS, payload)
    return token, expires_at


async def resolve_session(token: str) -> Session | None:
    """Look up the session bound to a token. None if absent/expired/malformed."""
    if not token:
        return None
    raw = await get_redis().get(f"{SESSION_KEY_PREFIX}{token}")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None  # legacy plain-wallet entries — force re-auth
    wallet = data.get("wallet")
    identity_id = data.get("identity_id")
    if not wallet or not identity_id:
        return None
    ttl = await get_redis().ttl(f"{SESSION_KEY_PREFIX}{token}")
    issued_at = int(time.time()) - (SESSION_TTL_SECONDS - max(ttl, 0))
    return Session(wallet=wallet, identity_id=identity_id, issued_at=issued_at)


async def revoke_session(token: str) -> None:
    await get_redis().delete(f"{SESSION_KEY_PREFIX}{token}")
