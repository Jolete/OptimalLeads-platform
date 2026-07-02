from __future__ import annotations

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from core_infrastructure.settings.settings import BrokerSettings, PersistenceSettings
from projects.optimalleads.leads.infrastructure.persistence.constants import LEADS_ENV_FILE


class LeadsSettings(PersistenceSettings, BrokerSettings):
    model_config = SettingsConfigDict(env_file=LEADS_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    telemetry_service_name: str


@lru_cache
def get_settings() -> LeadsSettings:
    return LeadsSettings()