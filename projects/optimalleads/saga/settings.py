from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import SAGA_ENV_FILE


class SagaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=SAGA_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    internal_service_protocol: Literal["rest", "grpc"]
    saga_database_url: str
    leads_api_base_url: str
    analytics_api_base_url: str
    leads_grpc_target: str
    analytics_grpc_target: str


@lru_cache
def get_settings() -> SagaSettings:
    return SagaSettings()