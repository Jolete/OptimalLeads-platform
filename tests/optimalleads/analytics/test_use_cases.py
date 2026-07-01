from __future__ import annotations

import pytest

from core_domain.contracts import EventEnvelope
from projects.optimalleads.analytics.application.use_cases import IngestEventsUseCase, ReadSnapshotUseCase
from projects.optimalleads.analytics.infrastructure.memory import InMemoryAnalyticsEventSource, InMemoryAnalyticsStore


@pytest.mark.asyncio
async def test_ingest_conversation_created_updates_snapshot() -> None:
    event_source = InMemoryAnalyticsEventSource()
    store = InMemoryAnalyticsStore()
    use_case = IngestEventsUseCase(event_source, store)

    await use_case.execute(
        EventEnvelope(
            event_id="evt-1",
            aggregate_id="conv-1",
            event_name="ConversationCreated",
            correlation_id="corr-1",
            causation_id=None,
            payload={"conversation_id": "conv-1", "title": "Sales"},
        )
    )

    snapshot = await ReadSnapshotUseCase(store).execute()
    assert snapshot.conversations["conv-1"].title == "Sales"


@pytest.mark.asyncio
async def test_ingest_lead_stage_changed_updates_snapshot() -> None:
    event_source = InMemoryAnalyticsEventSource()
    store = InMemoryAnalyticsStore()
    use_case = IngestEventsUseCase(event_source, store)

    await use_case.execute(
        EventEnvelope(
            event_id="evt-2",
            aggregate_id="lead-1",
            event_name="LeadCreated",
            correlation_id="corr-2",
            causation_id=None,
            payload={"lead_id": "lead-1", "name": "Acme"},
        )
    )
    await use_case.execute(
        EventEnvelope(
            event_id="evt-3",
            aggregate_id="lead-1",
            event_name="LeadStageChanged",
            correlation_id="corr-3",
            causation_id=None,
            payload={"lead_id": "lead-1", "stage": "qualified"},
        )
    )

    snapshot = await ReadSnapshotUseCase(store).execute()
    assert snapshot.leads["lead-1"].stage == "qualified"
