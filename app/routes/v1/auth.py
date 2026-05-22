"""POST /api/v1/auth — verify a SIWE-style signature and issue a session token.

Now also upserts into public.identities so signal-spectrum is a first-class
consumer of the identity layer (same DB, separate schema, shared identities).
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import Response

from app.auth import (
    issue_session,
    resolve_identity,
    revoke_session,
    validate_timestamp,
    verify_signature,
)
from app.deps import AuthSession, DbConn
from app.models import AuthRequest, AuthResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", response_model=AuthResponse)
async def authenticate(
    body: AuthRequest,
    conn: DbConn,
    x_nwo_wallet: Annotated[str | None, Header(alias="X-NWO-Wallet")] = None,
    x_nwo_signature: Annotated[str | None, Header(alias="X-NWO-Signature")] = None,
) -> AuthResponse:
    if not x_nwo_wallet or not x_nwo_signature:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="missing X-NWO-Wallet or X-NWO-Signature header",
        )
    try:
        validate_timestamp(body.timestamp)
        wallet = verify_signature(x_nwo_wallet, body.message, x_nwo_signature)
    except ValueError as exc:
        logger.info("auth rejected: %s", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid signature") from exc

    # First-signin = create identity in public.identities; subsequent signins reuse it.
    identity_id = await resolve_identity(conn, wallet)
    token, expires_at = await issue_session(wallet, identity_id)
    return AuthResponse(
        wallet=wallet, identity_id=identity_id, token=token, expires_at=expires_at
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout(
    session: AuthSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Response:
    if authorization and authorization.lower().startswith("bearer "):
        await revoke_session(authorization.split(" ", 1)[1].strip())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
async def me(session: AuthSession) -> dict:
    return {
        "wallet": session.wallet,
        "identity_id": session.identity_id,
        "issued_at": session.issued_at,
    }
