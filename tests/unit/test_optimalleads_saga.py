from __future__ import annotations

from core_domain import EventEnvelope, EventKind
from projects.optimalleads.saga.process_manager import OptimalLeadsSaga


class FakeAnalyticsClient:
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    async def ingest_event(self, event: EventEnvelope) -> dict[str, object]:
        self.events.append(event)
        return {"status": "ingested"}


class FakeLeadClient:
    def __init__(self) -> None:
        self.requests: list[dict[str, str]] = []

    async def create_lead_from_conversation(self, conversation_id: str, title: str, correlation_id: str) -> dict[str, object]:
        payload = {"conversation_id": conversation_id, "title": title, "correlation_id": correlation_id}
        self.requests.append(payload)
        return payload


class FakeStateRepository:
    def __init__(self) -> None:
        self.processed: set[str] = set()

    async def has_processed(self, event_id: str) -> bool:
        return event_id in self.processed

    async def mark_processed(self, event: EventEnvelope) -> None:
        self.processed.add(event.event_id)


def make_event(event_name: str, payload: dict[str, object]) -> EventEnvelope:
    return EventEnvelope(
        event_id=f"{event_name}-1",
        aggregate_id="aggregate-1",
        event_name=event_name,
        event_kind=EventKind.DOMAIN,
        correlation_id="correlation-1",
        causation_id=None,
        occurred_at="2026-07-09T00:00:00+00:00",
        payload=payload,
    )


async def test_conversation_created_creates_lead_ingests_analytics_and_flushes_leads_outbox() -> None:
    leads_client = FakeLeadClient()
    analytics_client = FakeAnalyticsClient()
    saga = OptimalLeadsSaga(leads_client, analytics_client)

    event = make_event("ConversationCreated", {"conversation_id": "conversation-1", "title": "ACME"})

    await saga.handle(event)

    assert analytics_client.events == [event]
    assert leads_client.requests == [
        {"conversation_id": "conversation-1", "title": "ACME", "correlation_id": "correlation-1"}
    ]


async def test_lead_created_is_ingested_by_analytics() -> None:
    leads_client = FakeLeadClient()
    analytics_client = FakeAnalyticsClient()
    saga = OptimalLeadsSaga(leads_client, analytics_client)
    event = make_event("LeadCreated", {"lead_id": "lead-1", "name": "ACME"})

    await saga.handle(event)

    assert analytics_client.events == [event]
    assert leads_client.requests == []


async def test_duplicate_events_are_ignored() -> None:
    leads_client = FakeLeadClient()
    analytics_client = FakeAnalyticsClient()
    saga = OptimalLeadsSaga(leads_client, analytics_client)
    event = make_event("LeadCreated", {"lead_id": "lead-1", "name": "ACME"})

    await saga.handle(event)
    await saga.handle(event)

    assert analytics_client.events == [event]


async def test_processed_events_are_checked_in_saga_state_repository() -> None:
    leads_client = FakeLeadClient()
    analytics_client = FakeAnalyticsClient()
    state_repository = FakeStateRepository()
    event = make_event("LeadCreated", {"lead_id": "lead-1", "name": "ACME"})
    state_repository.processed.add(event.event_id)
    saga = OptimalLeadsSaga(leads_client, analytics_client, state_repository=state_repository)

    await saga.handle(event)

    assert analytics_client.events == []