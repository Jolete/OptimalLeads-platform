from __future__ import annotations

from typing import Protocol, runtime_checkable

from core_domain.contracts.event_envelope import EventEnvelope


@runtime_checkable
class MessageBrokerPort(Protocol):
    async def publish(self, event: EventEnvelope) -> None:
        ...