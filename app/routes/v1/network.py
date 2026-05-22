"""/api/v1/network — agent network coordination."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.config import get_settings
from app.deps import AuthSession, DbConn
from app.models import TaskSubmit, VoteSubmit
from app.redis_client import broadcast

router = APIRouter(prefix="/network", tags=["network"])

CONSENSUS_THRESHOLD = 0.67  # 2/3 majority


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_network(conn: DbConn, session: AuthSession) -> dict[str, Any]:
    """Mark this wallet as a network participant. Idempotent."""
    await conn.execute(
        """
        INSERT INTO network_members (wallet, joined_at)
        VALUES ($1, NOW())
        ON CONFLICT (wallet) DO UPDATE SET last_active = NOW()
        """,
        session.wallet,
    )
    return {"wallet": session.wallet, "status": "joined"}


@router.get("/tasks")
async def list_tasks(
    conn: DbConn,
    session: AuthSession,
    open_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=500),
) -> list[dict[str, Any]]:
    where = "WHERE resolved_at IS NULL" if open_only else ""
    rows = await conn.fetch(
        f"""
        SELECT id, type, signal_id, proposed_class, evidence, payload,
               submitter_wallet, created_at, resolved_at, consensus_result
        FROM consensus_tasks
        {where}
        ORDER BY created_at DESC
        LIMIT $1
        """,
        limit,
    )
    out = []
    for r in rows:
        d = dict(r)
        for f in ("evidence", "payload", "consensus_result"):
            if d.get(f) and isinstance(d[f], str):
                d[f] = json.loads(d[f])
        out.append(d)
    return out


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def submit_task(
    body: TaskSubmit, conn: DbConn, session: AuthSession
) -> dict[str, Any]:
    row = await conn.fetchrow(
        """
        INSERT INTO consensus_tasks (
            type, signal_id, proposed_class, evidence, payload, submitter_wallet
        ) VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6)
        RETURNING id, created_at
        """,
        body.type,
        body.signal_id,
        body.proposed_class,
        json.dumps(body.evidence),
        json.dumps(body.payload or {}),
        session.wallet,
    )
    task = {
        "id": row["id"],
        "type": body.type,
        "signal_id": body.signal_id,
        "proposed_class": body.proposed_class,
        "submitter_wallet": session.wallet,
        "created_at": row["created_at"],
    }
    await broadcast("consensus:tasks", task)
    return task


@router.post("/vote")
async def vote(body: VoteSubmit, conn: DbConn, session: AuthSession) -> dict[str, Any]:
    # One vote per wallet per task.
    await conn.execute(
        """
        INSERT INTO consensus_votes (task_id, voter_wallet, classification, confidence, notes)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (task_id, voter_wallet) DO UPDATE
          SET classification = EXCLUDED.classification,
              confidence     = EXCLUDED.confidence,
              notes          = EXCLUDED.notes,
              cast_at        = NOW()
        """,
        body.task_id,
        session.wallet,
        body.classification,
        body.confidence,
        body.notes,
    )
    await broadcast(
        "consensus:vote",
        {"task_id": body.task_id, "voter": session.wallet, "classification": body.classification},
    )

    # Re-evaluate consensus after every vote.
    result = await _evaluate_consensus(conn, body.task_id)
    return {"task_id": body.task_id, "vote": "recorded", "consensus": result}


@router.get("/consensus/{task_id}")
async def get_consensus(task_id: int, conn: DbConn, session: AuthSession) -> dict[str, Any]:
    return await _evaluate_consensus(conn, task_id)


async def _evaluate_consensus(conn, task_id: int) -> dict[str, Any]:
    """Tally weighted votes; if any classification crosses the threshold, mark task resolved."""
    rows = await conn.fetch(
        """
        SELECT classification, confidence
        FROM consensus_votes
        WHERE task_id = $1
        """,
        task_id,
    )
    if not rows:
        return {"status": "no_votes", "votes": 0}

    weighted: dict[str, float] = {}
    total = 0.0
    for r in rows:
        w = float(r["confidence"])
        weighted[r["classification"]] = weighted.get(r["classification"], 0.0) + w
        total += w

    if total <= 0:
        return {"status": "no_weight", "votes": len(rows)}

    leader = max(weighted, key=weighted.get)
    leader_share = weighted[leader] / total

    result = {
        "status": "consensus" if leader_share >= CONSENSUS_THRESHOLD else "voting",
        "votes": len(rows),
        "leader": leader,
        "leader_share": round(leader_share, 4),
        "tallies": {k: round(v, 4) for k, v in weighted.items()},
    }

    if result["status"] == "consensus":
        await conn.execute(
            """
            UPDATE consensus_tasks
            SET resolved_at = NOW(), consensus_result = $1::jsonb
            WHERE id = $2 AND resolved_at IS NULL
            """,
            json.dumps(result),
            task_id,
        )

    return result
