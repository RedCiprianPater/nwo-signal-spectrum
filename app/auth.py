"""Web3 authentication.

Mirrors the SIWE-style flow used by the React frontend:
  1. Client signs `{prefix}\n{domain}\n{nonce}\n{timestamp}` with ethers.signMessage()
  2. Client POSTs to /api/v1/auth with headers X-NWO-Wallet, X-NWO-Signature and body { message, timestamp }
  3. Server recovers the signing address with eth_account, compares to X-NWO-Wallet
  4. On success, server issues a session token cached in Redis (1h TTL)
  5. Subsequent requests use `Authorization: Bearer <token>`

Why a session token at all when the client could re-sign every request?
  - MetaMask popup prompts are jarring; sessionStorage caches are routine.
  - Keeps the server's hot path (one Redis GET) cheap.
"""
from __future__ import annotations

import logging
import secrets
import time
from dataclasses import dataclass

from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import is_checksum_address, to_checksum_address

from app.config import get_settings
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

SESSION_TTL_SECONDS = 60 * 60  # 1 hour
SESSION_KEY_PREFIX = "session:"


@dataclass(frozen=True)
class Session:
    wallet: str  # checksum-cased
    issued_at: int


def _normalize_address(addr: str) -> str:
    """Force checksum casing; raise ValueError if not a valid address."""
    if not addr:
        raise ValueError("empty address")
    # eth_utils accepts any case; convert to canonical EIP-55.
    return to_checksum_address(addr)


def verify_signature(wallet: str, message: str, signature: str) -> str:
    """Recover address from a personal_sign signature and compare to claimed wallet.

    Returns the recovered (checksum) address on success.
    Raises ValueError on mismatch or malformed input.
    """
    claimed = _normalize_address(wallet)
    encoded = encode_defunct(text=message)
    try:
        recovered = Account.recover_message(encoded, signature=signature)
    except Exception as exc:  # bad signature format, etc.
        raise ValueError(f"signature recovery failed: {exc}") from exc

    if to_checksum_address(recovered) != claimed:
        raise ValueError("signature does not match claimed wallet")
    return claimed


def validate_timestamp(timestamp: int) -> None:
    """Reject signed messages whose timestamp is outside the configured window."""
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


# ----- Session token storage (Redis) -----

async def issue_session(wallet: str) -> tuple[str, int]:
    """Generate a random session token, store wallet binding in Redis. Returns (token, expires_at)."""
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    await get_redis().setex(
        f"{SESSION_KEY_PREFIX}{token}",
        SESSION_TTL_SECONDS,
        _normalize_address(wallet),
    )
    return token, expires_at


async def resolve_session(token: str) -> Session | None:
    """Look up the wallet bound to a session token. None if absent/expired."""
    if not token:
        return None
    wallet = await get_redis().get(f"{SESSION_KEY_PREFIX}{token}")
    if not wallet:
        return None
    ttl = await get_redis().ttl(f"{SESSION_KEY_PREFIX}{token}")
    issued_at = int(time.time()) - (SESSION_TTL_SECONDS - max(ttl, 0))
    return Session(wallet=wallet, issued_at=issued_at)


async def revoke_session(token: str) -> None:
    await get_redis().delete(f"{SESSION_KEY_PREFIX}{token}")
