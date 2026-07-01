from __future__ import annotations

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from core_infrastructure.settings.settings import BrokerSettings, PersistenceSettings


class ChatSettings(PersistenceSettings, BrokerSettings):
    model_config = SettingsConfigDict(env_file="projects/optimalleads/chat/.env", env_file_encoding="utf-8", extra="ignore")

    telemetry_service_name: str

    @property
    def chat_database_url(self) -> str:
        return self.business_database_url


@lru_cache
def get_settings() -> ChatSettings:
    return ChatSettings()