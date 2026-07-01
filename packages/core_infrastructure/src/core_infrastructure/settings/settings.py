from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class PersistenceSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    persistence_provider: Literal["memory", "sqlite", "sqlserver"]
    reset_database_on_startup: bool = False
    business_database_url: str
    outbox_database_url: str | None = None
    audit_database_url: str | None = None
    events_database_url: str | None = None
    outbox_table_name: str | None = None

    @property
    def effective_outbox_database_url(self) -> str:
        return self.outbox_database_url or self.business_database_url

    @property
    def effective_audit_database_url(self) -> str:
        return self.audit_database_url or self.business_database_url

    @property
    def effective_events_database_url(self) -> str:
        return self.events_database_url or self.business_database_url

    @property
    def effective_outbox_table_name(self) -> str:
        return self.outbox_table_name or "outbox"


class BrokerSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    broker_provider: Literal["in_memory", "faststream_kafka", "faststream_rabbitmq", "faststream_azure_service_bus"]
    broker_url: str
    broker_topic: str
    broker_queue: str
    broker_consumer_group: str


class Settings(BaseSettings):
    app_name: str = "quantion"