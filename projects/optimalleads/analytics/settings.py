from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import SettingsConfigDict

from core_infrastructure.settings.settings import BrokerSettings, PersistenceSettings
from projects.optimalleads.analytics.infrastructure.persistence.constants import ANALYTICS_ENV_FILE


class AnalyticsSettings(PersistenceSettings, BrokerSettings):
    model_config = SettingsConfigDict(env_file=ANALYTICS_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    telemetry_service_name: str
    internal_service_protocol: Literal["rest", "grpc"]
    grpc_listen_host: str
    grpc_listen_port: int

@lru_cache
def get_settings() -> AnalyticsSettings:
    return AnalyticsSettings()