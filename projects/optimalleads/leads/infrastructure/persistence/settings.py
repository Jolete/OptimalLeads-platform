from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from core_infrastructure.settings.settings import PersistenceSettings


class LeadsPersistenceSettings(PersistenceSettings):
    model_config = SettingsConfigDict(
        env_file="projects/optimalleads/leads/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telemetry_service_name: str


@lru_cache
def get_persistence_settings() -> LeadsPersistenceSettings:
    return LeadsPersistenceSettings()
