from __future__ import annotations

from typing import Any, Protocol

from core_domain import EventEnvelope


class EventDecoder(Protocol):
    def __call__(self, message: Any) -> EventEnvelope: ...


class SagaBridgePort(Protocol):
    async def handle(self, event: EventEnvelope) -> None: ...


class SagaEventHandler(Protocol):
    async def __call__(self, event: EventEnvelope) -> None: ...


class RetryPolicy(Protocol):
    def should_retry(self, attempt: int) -> bool: ...

    def next_delay_seconds(self, attempt: int) -> float: ...


class DeadLetterPublisher(Protocol):
    async def publish(self, event: EventEnvelope, reason: str) -> None: ...


class BrokerTransportPort(Protocol):
    async def start(self) -> None: ...

    async def close(self) -> None: ...

    def subscriber(self, *args: Any, **kwargs: Any): ...

    async def publish(self, *args: Any, **kwargs: Any): ...


class BrokerFactory(Protocol):
    def build_chat_broker(self, broker_url: str) -> BrokerTransportPort: ...

    def build_leads_broker(self, broker_url: str) -> BrokerTransportPort: ...
