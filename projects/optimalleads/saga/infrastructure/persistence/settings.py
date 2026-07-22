from __future__ import annotations

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from core_infrastructure.settings.settings import PersistenceSettings
from projects.optimalleads.saga.constants import SAGA_ENV_FILE


class SagaPersistenceSettings(PersistenceSettings):
    model_config = SettingsConfigDict(
        env_file=SAGA_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telemetry_service_name: str


@lru_cache
def get_persistence_settings() -> SagaPersistenceSettings:
    return SagaPersistenceSettings()
