from __future__ import annotations

from dataclasses import dataclass

from .protocols import DeadLetterPublisher, EventDecoder, SagaAttemptRecorder, SagaEventHandler
from .retry.protocols import RetryPolicy
from .retry.config import BaseRetrySettings


@dataclass(slots=True)
class SagaRoutePlan:
    name: str
    enabled: bool
    consumer_group: str
    retry_topic: str
    dead_letter_target: str
    retry_settings: BaseRetrySettings


@dataclass(slots=True)
class SagaBridgeTopology:
    chat_broker_url: str
    chat_broker_topic: str
    chat_consumer_group: str
    leads_broker_url: str
    leads_broker_queue: str
    leads_consumer_group: str
    replay_topic: str
    chat_retry_topic: str
    leads_retry_queue: str
    chat_dead_letter_topic: str
    leads_dead_letter_queue: str
    enabled: bool = True
    route_chat_to_leads: bool = True
    route_events_to_analytics: bool = True


@dataclass(slots=True)
class SagaBridgeContract:
    inbound_chat: SagaRoutePlan
    inbound_leads: SagaRoutePlan


@dataclass(slots=True)
class SagaBridgeResponsibilities:
    decode_event: EventDecoder
    route_chat_event: SagaEventHandler
    route_leads_event: SagaEventHandler
    chat_retry_policy: RetryPolicy | None = None
    leads_retry_policy: RetryPolicy | None = None
    chat_dead_letter_publisher: DeadLetterPublisher | None = None
    leads_dead_letter_publisher: DeadLetterPublisher | None = None
    attempt_recorder: SagaAttemptRecorder | None = None


@dataclass(slots=True)
class SagaBridgeRuntime:
    chat_broker: object
    leads_broker: object
    chat_retry_policy: RetryPolicy | None
    leads_retry_policy: RetryPolicy | None
    chat_dead_letter_publisher: DeadLetterPublisher | None
    leads_dead_letter_publisher: DeadLetterPublisher | None


SagaBridgeRoutePlan = SagaRoutePlan
