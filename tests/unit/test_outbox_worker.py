from __future__ import annotations

import pytest

from core_domain import EventEnvelope, EventKind
from core_infrastructure.services import EventDispatcher, OutboxWorker


class MemoryOutbox:
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    async def add(self, event: EventEnvelope) -> None:
        self.events.append(event)

    async def drain(self) -> list[EventEnvelope]:
        return list(self.events)

    async def mark_published(self, events: list[EventEnvelope]) -> None:
        published_ids = {event.event_id for event in events}
        self.events = [event for event in self.events if event.event_id not in published_ids]


def make_event(event_id: str = "event-1") -> EventEnvelope:
    return EventEnvelope(
        event_id=event_id,
        aggregate_id="aggregate-1",
        event_name="ConversationCreated",
        event_kind=EventKind.DOMAIN,
        correlation_id="correlation-1",
        causation_id=None,
        occurred_at=None,
        payload={"conversation_id": "conversation-1"},
    )


@pytest.mark.asyncio
async def test_outbox_worker_marks_events_published_after_successful_dispatch() -> None:
    outbox = MemoryOutbox()
    event = make_event()
    await outbox.add(event)
    published: list[EventEnvelope] = []

    async def handler(current_event: EventEnvelope) -> None:
        published.append(current_event)

    dispatcher = EventDispatcher(default_handler=handler)
    worker = OutboxWorker(outbox, dispatcher)

    count = await worker.flush()

    assert count == 1
    assert published == [event]
    assert await outbox.drain() == []


@pytest.mark.asyncio
async def test_outbox_worker_keeps_event_when_dispatch_fails() -> None:
    outbox = MemoryOutbox()
    event = make_event()
    await outbox.add(event)

    async def failing_handler(current_event: EventEnvelope) -> None:
        raise RuntimeError("broker unavailable")

    dispatcher = EventDispatcher(default_handler=failing_handler)
    worker = OutboxWorker(outbox, dispatcher)

    with pytest.raises(RuntimeError, match="broker unavailable"):
        await worker.flush()

    assert await outbox.drain() == [event]