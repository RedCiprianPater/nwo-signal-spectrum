"""Global geographic layers — GeoLibre integration.

Exposes /api/v1/layers/* endpoints backed by the spectrum.* tables
created by global_layers_schema.sql + global_layers_seed.sql.

Read endpoints (list, bbox, entity detail, nuclear summary) require
nothing beyond a healthy database pool. The cron endpoints
(refresh-due, bootstrap-country) are protected by a shared bearer
token (INTERNAL_CRON_TOKEN) and try to import the ingester service
module; if it isn't installed yet they return a clear
"not configured" response instead of crashing, so the app boots
cleanly whether or not the ingester code is in the repo.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.db import get_pool

log = logging.getLogger(__name__)

# ----------------------------------------------------------------
# Optional orchestrator import — degrade gracefully if not present
# ----------------------------------------------------------------
try:
    from app.services import data_streams_orchestrator  # type: ignore
    _ORCHESTRATOR_AVAILABLE = True
    log.info("layers: data_streams_orchestrator loaded")
except Exception as _e:
    log.warning("layers: data_streams_orchestrator not available (%s) — "
                "cron endpoints will return 'not configured' until installed", _e)
    data_streams_orchestrator = None  # type: ignore
    _ORCHESTRATOR_AVAILABLE = False

router = APIRouter(prefix="/layers", tags=["layers"])


# ================================================================
# Models
# ================================================================

class LayerInfo(BaseModel):
    id: str
    category: str
    label: str
    color: str
    geometry_type: str
    is_realtime: bool
    refresh_minutes: Optional[int] = None
    source: Optional[str] = None
    description: Optional[str] = None
    entity_count: int = 0
    last_run_at: Optional[str] = None


class BboxRequest(BaseModel):
    min_lat: float = Field(ge=-90, le=90)
    min_lon: float = Field(ge=-180, le=180)
    max_lat: float = Field(ge=-90, le=90)
    max_lon: float = Field(ge=-180, le=180)
    layers: list[str]
    limit_per_layer: int = Field(default=2500, ge=1, le=10000)


class BboxResponse(BaseModel):
    layers: dict[str, list[dict[str, Any]]]
    counts: dict[str, int]


class EntityDetail(BaseModel):
    layer: str
    entity: dict[str, Any]
    annotations: list[dict[str, Any]] = []


class BootstrapRequest(BaseModel):
    iso2: str = Field(min_length=2, max_length=2)


# ================================================================
# Layer → table mapping
# ================================================================
LAYER_TABLES = {
    # defence
    "military_bases":           "spectrum.military_bases",
    "defence_positions":        "spectrum.defence_positions",
    "nuclear_sites":            "spectrum.nuclear_sites",
    "intelligence_buildings":   "spectrum.intelligence_buildings",
    # energy
    "power_plants":             "spectrum.power_plants",
    "power_lines":              "spectrum.power_lines",
    "transformer_stations":     "spectrum.transformer_stations",
    "pipelines":                "spectrum.pipelines",
    # comms
    "submarine_cables":         "spectrum.submarine_cables",
    "cell_towers":              "spectrum.cell_towers",
    "radio_towers":             "spectrum.radio_towers",
    "satellites":               "spectrum.satellites",
    # transport
    "flight_tracks":            "spectrum.flight_tracks",
    "shipping_routes":          "spectrum.shipping_routes",
    "ship_positions":           "spectrum.ship_positions",
    # environment
    "weather_observations":     "spectrum.weather_observations",
    "geological_events":        "spectrum.geological_events",
    "ocean_observations":       "spectrum.ocean_observations",
    "atmospheric_observations": "spectrum.atmospheric_observations",
    # institutions
    "hospitals":                "spectrum.hospitals",
    "research_labs":            "spectrum.research_labs",
    "data_centers":             "spectrum.data_centers",
    "embassies":                "spectrum.embassies",
    "government_buildings":     "spectrum.government_buildings",
    "police_stations":          "spectrum.police_stations",
    # science
    "particle_accelerators":    "spectrum.particle_accelerators",
    "physics_experiments":      "spectrum.physics_experiments",
    # industry
    "robot_manufacturers":      "spectrum.robot_manufacturers",
}

LINE_LAYERS = {"pipelines", "power_lines", "submarine_cables", "shipping_routes"}


# ================================================================
# Helpers
# ================================================================
def _jsonable(d: dict) -> dict:
    """Coerce asyncpg row values into JSON-serializable Python."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if v is None:
            out[k] = None
        elif isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        elif isinstance(v, Decimal):
            out[k] = float(v)
        elif isinstance(v, (bytes, bytearray, memoryview)):
            # PostGIS WKB blobs and similar — drop, the client doesn't need them
            continue
        else:
            out[k] = v
    return out


def _check_internal_token(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get("INTERNAL_CRON_TOKEN")
    if not expected:
        raise HTTPException(503, "INTERNAL_CRON_TOKEN not configured on the server")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    if authorization[7:].strip() != expected:
        raise HTTPException(403, "invalid token")


# ================================================================
# Endpoints — reads
# ================================================================

@router.get("", response_model=list[LayerInfo])
async def list_layers() -> list[dict]:
    """Return registered layers with their current entity counts.

    Reads from spectrum.layers. If that table doesn't exist yet (migration
    not applied), returns an empty list rather than 500ing — the frontend
    keeps its baked fallback registry.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
                select
                    id, category, label, color, geometry_type,
                    is_realtime, refresh_minutes, source, description,
                    coalesce((metadata->>'entity_count')::int, 0)        as entity_count,
                    (metadata->>'last_run_at')                            as last_run_at
                from spectrum.layers
                order by category, label
            """)
        except Exception as e:
            log.warning("list_layers: spectrum.layers not queryable (%s)", e)
            return []
    return [_jsonable(dict(r)) for r in rows]


@router.post("/bbox", response_model=BboxResponse)
async def layers_bbox(req: BboxRequest) -> dict:
    """Query one or more layers for entities inside a bbox.

    Point layers are filtered by lat/lon columns; line layers are filtered
    by PostGIS ST_Intersects with an envelope, and the geometry is shipped
    back as GeoJSON LineString coordinates.
    """
    pool = get_pool()
    out: dict[str, list[dict]] = {}
    counts: dict[str, int] = {}

    async with pool.acquire() as conn:
        for layer_id in req.layers:
            table = LAYER_TABLES.get(layer_id)
            if not table:
                out[layer_id] = []
                counts[layer_id] = 0
                continue
            try:
                if layer_id in LINE_LAYERS:
                    rows = await conn.fetch(f"""
                        select
                            id, name,
                            coalesce(properties, '{{}}'::jsonb)        as properties,
                            st_asgeojson(geom::geometry)::jsonb        as geometry
                        from {table}
                        where st_intersects(
                            geom::geometry,
                            st_makeenvelope($1, $2, $3, $4, 4326)
                        )
                        limit $5
                    """, req.min_lon, req.min_lat, req.max_lon, req.max_lat, req.limit_per_layer)
                else:
                    rows = await conn.fetch(f"""
                        select *
                        from {table}
                        where lat between $1 and $2
                          and lon between $3 and $4
                        limit $5
                    """, req.min_lat, req.max_lat, req.min_lon, req.max_lon, req.limit_per_layer)

                items = [_jsonable(dict(r)) for r in rows]
                out[layer_id] = items
                counts[layer_id] = len(items)
            except Exception as e:
                log.warning("bbox query failed for %s (%s)", layer_id, e)
                out[layer_id] = []
                counts[layer_id] = 0

    return {"layers": out, "counts": counts}


@router.get("/nuclear/summary")
async def nuclear_summary() -> dict:
    """Aggregate nuclear arsenal totals across states."""
    pool = get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval("""
            select 1 from information_schema.tables
            where table_schema='spectrum' and table_name='nuclear_arsenals'
        """)
        if not exists:
            return {"totals": {}, "states": []}
        states = await conn.fetch("""
            select *
            from spectrum.nuclear_arsenals
            order by warheads desc nulls last
        """)
    rows = [_jsonable(dict(s)) for s in states]
    totals = {
        "total_warheads":    sum((s.get("warheads") or 0)  for s in rows),
        "deployed_warheads": sum((s.get("deployed") or 0)  for s in rows),
        "declared_states":   sum(1 for s in rows if s.get("is_declared")),
        "undeclared_states": sum(1 for s in rows if not s.get("is_declared")),
    }
    return {"totals": totals, "states": rows}


@router.get("/{layer_id}/{entity_id}", response_model=EntityDetail)
async def entity_detail(layer_id: str, entity_id: int) -> dict:
    """Return one entity plus its annotations."""
    table = LAYER_TABLES.get(layer_id)
    if not table:
        raise HTTPException(404, f"unknown layer: {layer_id}")

    pool = get_pool()
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(f"select * from {table} where id=$1", entity_id)
        except Exception as e:
            log.warning("entity_detail: query failed for %s/%s (%s)", layer_id, entity_id, e)
            raise HTTPException(500, f"query failed: {e}")
        if not row:
            raise HTTPException(404, "entity not found")

        annots: list[dict] = []
        try:
            ann_rows = await conn.fetch("""
                select
                    id, annotation_type, body, submitter_identity_id, created_at
                from spectrum.layer_annotations
                where layer_id=$1 and entity_id=$2
                order by created_at desc
                limit 50
            """, layer_id, entity_id)
            annots = [_jsonable(dict(a)) for a in ann_rows]
        except Exception as e:
            log.debug("annotations unavailable for %s/%s: %s", layer_id, entity_id, e)

    return {
        "layer":       layer_id,
        "entity":      _jsonable(dict(row)),
        "annotations": annots,
    }


# ================================================================
# Endpoints — cron (INTERNAL_CRON_TOKEN)
# ================================================================

@router.post("/refresh-due")
async def refresh_due(_authed: None = Depends(_check_internal_token)) -> dict:
    """Refresh all realtime layers whose refresh_minutes window has elapsed."""
    if not _ORCHESTRATOR_AVAILABLE:
        return {
            "ok": False,
            "reason": "data_streams_orchestrator service not installed yet",
            "hint": "place app/services/data_streams_orchestrator.py and the external_feeds package in the repo",
            "refreshed": [],
        }
    try:
        result = await data_streams_orchestrator.refresh_due(get_pool())
        return {"ok": True, **(result or {})}
    except Exception as e:
        log.exception("refresh_due failed")
        raise HTTPException(500, f"refresh failed: {e}")


@router.post("/bootstrap-country")
async def bootstrap_country(
    req: BootstrapRequest,
    _authed: None = Depends(_check_internal_token),
) -> dict:
    """Pull OSM-backed layers for a country into spectrum.* tables."""
    if not _ORCHESTRATOR_AVAILABLE:
        return {
            "ok": False,
            "reason": "data_streams_orchestrator service not installed yet",
            "hint": "place app/services/data_streams_orchestrator.py and the external_feeds package in the repo",
            "iso2": req.iso2.upper(),
        }
    try:
        result = await data_streams_orchestrator.bootstrap_country(
            get_pool(), req.iso2.upper()
        )
        return {"ok": True, "iso2": req.iso2.upper(), **(result or {})}
    except Exception as e:
        log.exception("bootstrap_country failed")
        raise HTTPException(500, f"bootstrap failed: {e}")
