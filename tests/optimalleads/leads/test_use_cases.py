from __future__ import annotations

import pytest

from projects.optimalleads.leads.application.use_cases import AdvanceLeadStageUseCase, CreateLeadUseCase
from projects.optimalleads.leads.infrastructure.memory import InMemoryLeadOutbox, InMemoryLeadRepository


@pytest.mark.asyncio
async def test_create_lead_publishes_created_event() -> None:
    repository = InMemoryLeadRepository()
    outbox = InMemoryLeadOutbox()
    use_case = CreateLeadUseCase(repository, outbox)

    lead = await use_case.execute("Acme")

    assert lead.name.value == "Acme"
    events = await outbox.drain()
    assert len(events) == 1
    assert events[0].event_name == "LeadCreated"


@pytest.mark.asyncio
async def test_advance_stage_publishes_stage_changed_event() -> None:
    repository = InMemoryLeadRepository()
    outbox = InMemoryLeadOutbox()
    create_use_case = CreateLeadUseCase(repository, outbox)
    advance_use_case = AdvanceLeadStageUseCase(repository, outbox)

    lead = await create_use_case.execute("Acme")
    updated = await advance_use_case.execute(str(lead.id.value), "qualified")

    assert updated.stage.value == "qualified"
    events = await outbox.drain()
    assert len(events) == 2
    assert events[-1].event_name == "LeadStageChanged"
