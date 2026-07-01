from __future__ import annotations

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from core_infrastructure.settings.settings import BrokerSettings, PersistenceSettings


class LeadsSettings(PersistenceSettings, BrokerSettings):
    model_config = SettingsConfigDict(env_file="projects/optimalleads/leads/.env", env_file_encoding="utf-8", extra="ignore")

    telemetry_service_name: str

    @property
    def effective_outbox_database_url(self) -> str:
        return self.outbox_database_url or self.business_database_url

    @property
    def effective_audit_database_url(self) -> str:
        return self.audit_database_url or self.business_database_url

    @property
    def effective_events_database_url(self) -> str:
        return self.events_database_url or self.business_database_url


@lru_cache
def get_settings() -> LeadsSettings:
    return LeadsSettings()