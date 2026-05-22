"""/api/v1/agents — list online agents, register a new agent.

Agents now FK into public.identities. Registration is upsert-by-identity rather
than upsert-by-wallet — one identity can have exactly one agent profile.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from app.config import get_settings
from app.deps import AuthSession, DbConn
from app.models import AgentRecord, AgentRegister
from app.redis_client import broadcast

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRecord])
async def list_agents(
    conn: DbConn,
    session: AuthSession,
    online_only: bool = Query(True),
    region: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> list[AgentRecord]:
    clauses: list[str] = []
    params: list = []
    if online_only:
        clauses.append("last_seen > NOW() - INTERVAL '5 minutes'")
    if region:
        params.append(region)
        clauses.append(f"region = ${len(params)}")
    where = "WHERE " + " AND ".join(clauses) if clauses else ""

    params.append(limit)
    rows = await conn.fetch(
        f"""
        SELECT id, identity_id::text, wallet, capabilities, region, last_seen,
               (last_seen > NOW() - INTERVAL '5 minutes') AS online
        FROM agents
        {where}
        ORDER BY last_seen DESC
        LIMIT ${len(params)}
        """,
        *params,
    )
    return [AgentRecord(**dict(r)) for r in rows]


@router.post("", response_model=AgentRecord, status_code=status.HTTP_201_CREATED)
async def register_agent(
    body: AgentRegister, conn: DbConn, session: AuthSession
) -> AgentRecord:
    settings = get_settings()
    if settings.agent_allowlist_set and session.wallet.lower() not in settings.agent_allowlist_set:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="wallet not in agent allowlist")

    row = await conn.fetchrow(
        """
        INSERT INTO agents (identity_id, wallet, capabilities, region, last_seen)
        VALUES ($1::uuid, $2, $3, $4, NOW())
        ON CONFLICT (identity_id) DO UPDATE
          SET capabilities = EXCLUDED.capabilities,
              region       = EXCLUDED.region,
              wallet       = EXCLUDED.wallet,
              last_seen    = NOW()
        RETURNING id, identity_id::text, wallet, capabilities, region, last_seen,
                  (last_seen > NOW() - INTERVAL '5 minutes') AS online
        """,
        session.identity_id,
        session.wallet,
        body.capabilities,
        body.region,
    )
    record = AgentRecord(**dict(row))
    await broadcast("agents:online", record.model_dump(mode="json"))
    return record


@router.post("/heartbeat", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def heartbeat(conn: DbConn, session: AuthSession) -> Response:
    """Bump last_seen. Agents call this every ~60s to stay 'online'."""
    await conn.execute(
        "UPDATE agents SET last_seen = NOW() WHERE identity_id = $1::uuid",
        session.identity_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
