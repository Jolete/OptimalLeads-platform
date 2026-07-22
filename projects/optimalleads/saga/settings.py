from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core_infrastructure.settings.settings import PersistenceSettings
from .constants import SAGA_ENV_FILE, SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC, SAGA_INTERNAL_SERVICE_PROTOCOL_REST
from .bridge.retry.config import ChatRetrySettings, LeadsRetrySettings


class SagaSettings(PersistenceSettings):
    model_config = SettingsConfigDict(env_file=SAGA_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    internal_service_protocol: Literal[SAGA_INTERNAL_SERVICE_PROTOCOL_REST, SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC]
    leads_api_base_url: str
    analytics_api_base_url: str
    leads_grpc_target: str
    analytics_grpc_target: str
    chat_broker_url: str
    chat_broker_topic: str
    chat_consumer_group: str
    leads_broker_url: str
    leads_broker_queue: str
    leads_consumer_group: str
    chat_dead_letter_topic: str
    leads_dead_letter_queue: str
    saga_bridge_enabled: bool = True
    saga_bridge_route_chat_to_leads: bool = True
    saga_bridge_route_events_to_analytics: bool = True
    saga_bridge_replay_topic: str
    saga_bridge_chat_retry_topic: str
    saga_bridge_leads_retry_queue: str
    saga_bridge_chat_retry_max_attempts: int
    saga_bridge_chat_retry_backoff_seconds: float
    saga_bridge_chat_retry_jitter_seconds: float
    saga_bridge_chat_retry_timeout_seconds: float | None = None

    saga_bridge_leads_retry_max_attempts: int
    saga_bridge_leads_retry_backoff_seconds: float
    saga_bridge_leads_retry_jitter_seconds: float
    saga_bridge_leads_retry_timeout_seconds: float | None = None

    @field_validator("saga_bridge_chat_retry_timeout_seconds", "saga_bridge_leads_retry_timeout_seconds", mode="before")
    @classmethod
    def _empty_timeout_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @property
    def saga_bridge_chat_retry_settings(self) -> ChatRetrySettings:
        return ChatRetrySettings(
            max_attempts=self.saga_bridge_chat_retry_max_attempts,
            backoff_seconds=self.saga_bridge_chat_retry_backoff_seconds,
            jitter_seconds=self.saga_bridge_chat_retry_jitter_seconds,
            timeout_seconds=self.saga_bridge_chat_retry_timeout_seconds,
        )

    @property
    def saga_bridge_leads_retry_settings(self) -> LeadsRetrySettings:
        return LeadsRetrySettings(
            max_attempts=self.saga_bridge_leads_retry_max_attempts,
            backoff_seconds=self.saga_bridge_leads_retry_backoff_seconds,
            jitter_seconds=self.saga_bridge_leads_retry_jitter_seconds,
            timeout_seconds=self.saga_bridge_leads_retry_timeout_seconds,
        )


@lru_cache
def get_settings() -> SagaSettings:
    return SagaSettings()