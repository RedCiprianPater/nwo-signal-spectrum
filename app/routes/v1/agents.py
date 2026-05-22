"""/api/v1/agents — list online agents, register a new agent."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from app.config import get_settings
from app.deps import AuthSession, DbConn
from app.models import AgentRecord, AgentRegister
from app.redis_client import broadcast

router = APIRouter(prefix="/agents", tags=["agents"])

ONLINE_WINDOW_SECONDS = 300  # last 5 minutes


@router.get("", response_model=list[AgentRecord])
async def list_agents(
    conn: DbConn,
    session: AuthSession,
    online_only: bool = Query(True),
    region: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> list[AgentRecord]:
    clauses = []
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
        SELECT id, wallet, capabilities, region, last_seen,
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
        INSERT INTO agents (wallet, capabilities, region, last_seen)
        VALUES ($1, $2, $3, NOW())
        ON CONFLICT (wallet) DO UPDATE
          SET capabilities = EXCLUDED.capabilities,
              region       = EXCLUDED.region,
              last_seen    = NOW()
        RETURNING id, wallet, capabilities, region, last_seen,
                  (last_seen > NOW() - INTERVAL '5 minutes') AS online
        """,
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
        "UPDATE agents SET last_seen = NOW() WHERE wallet = $1", session.wallet
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
