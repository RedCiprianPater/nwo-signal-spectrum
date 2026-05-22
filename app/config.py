"""Application settings — loaded from environment / .env.

Everything that varies between dev/staging/prod lives here. No secrets in code.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Postgres / Supabase ---
    database_url: str = Field(..., description="Supabase Supavisor pooler URL (port 6543)")
    database_url_direct: str | None = Field(
        default=None, description="Direct/session-pooler URL for migrations only"
    )
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    # --- Redis ---
    redis_url: str = Field(..., description="Redis URL — rediss:// for TLS")

    # --- Web3 auth ---
    nwo_auth_domain: str = "nwo.capital"
    nwo_auth_message_prefix: str = "Authenticate for NWO Signal Spectrum"
    nwo_auth_timestamp_window: int = 300
    nwo_agent_allowlist: str = ""

    # --- Osiris ---
    osiris_api_url: str = "https://osiris.nwo.capital/api"
    osiris_api_key: str = ""
    osiris_timeout_seconds: float = 10.0

    # --- External signal APIs ---
    nasa_api_key: str = "DEMO_KEY"
    adsbexchange_api_key: str = ""
    usgs_feed_url: str = (
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson"
    )
    noaa_swpc_url: str = "https://services.swpc.noaa.gov/json"
    safecast_api_url: str = "https://api.safecast.org"

    # --- Notifications ---
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""

    # --- App ---
    log_level: str = "INFO"
    cors_origins: str = "https://nwo.capital"
    app_version: str = "2.0.0"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def agent_allowlist_set(self) -> set[str]:
        return {a.strip().lower() for a in self.nwo_agent_allowlist.split(",") if a.strip()}

    @field_validator("database_url")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgres://", "postgresql://")):
            raise ValueError("DATABASE_URL must be a postgres connection string")
        # asyncpg doesn't accept the 'postgres://' scheme — normalize.
        return v.replace("postgres://", "postgresql://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
