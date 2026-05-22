"""/api/v2/consensus — exposes consensus results and relays them to Osiris.

This is the v2 layer over the v1 network module. v1 is the single-network
consensus engine; v2 is "what does the wider Osiris network think + here's our
contribution".
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.deps import AuthSession, DbConn
from app.services import osiris

router = APIRouter(prefix="/consensus", tags=["v2:consensus"])


@router.get("/{task_id}")
async def get_consensus(
    task_id: int, conn: DbConn, session: AuthSession
) -> dict[str, Any]:
    row = await conn.fetchrow(
        """
        SELECT id, type, signal_id, proposed_class, resolved_at,
               consensus_result, created_at
        FROM consensus_tasks
        WHERE id = $1
        """,
        task_id,
    )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="task not found")
    return dict(row)


@router.post("/{task_id}/publish")
async def publish_to_osiris(
    task_id: int, conn: DbConn, session: AuthSession
) -> dict[str, Any]:
    """Push a resolved consensus task upstream to Osiris."""
    row = await conn.fetchrow(
        """
        SELECT id, type, signal_id, proposed_class, consensus_result
        FROM consensus_tasks
        WHERE id = $1 AND resolved_at IS NOT NULL
        """,
        task_id,
    )
    if row is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="resolved task not found"
        )
    osiris_response = await osiris.post_consensus(
        {
            "task_id": row["id"],
            "type": row["type"],
            "signal_id": row["signal_id"],
            "proposed_class": row["proposed_class"],
            "consensus_result": row["consensus_result"],
            "publisher_wallet": session.wallet,
        }
    )
    return {"published": osiris_response is not None, "osiris": osiris_response}


@router.get("/agents/online")
async def online_agents(conn: DbConn, session: AuthSession) -> dict[str, Any]:
    """Combined view: who's online here + Osiris federation status."""
    row = await conn.fetchrow(
        """
        SELECT COUNT(*)::int AS n
        FROM agents
        WHERE last_seen > NOW() - INTERVAL '5 minutes'
        """
    )
    return {
        "local_online": int(row["n"]) if row else 0,
        "federation": "osiris" if await osiris.fetch_threat_level() else "isolated",
    }
