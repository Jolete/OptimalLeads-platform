from __future__ import annotations

from typing import Protocol, runtime_checkable

from core_domain.contracts.event_envelope import EventEnvelope


@runtime_checkable
class OutboxPort(Protocol):
    """Generic outbox contract for persisted event envelopes.

    Each call to `add` stores one envelope. The `aggregate_id` identifies the
    domain aggregate that produced the event, while `event_id` identifies the
    envelope itself.
    """

    async def add(self, event: EventEnvelope) -> None:
        ...

    async def drain(self) -> list[EventEnvelope]:
        ...

    async def mark_published(self, events: list[EventEnvelope]) -> None:
        ...