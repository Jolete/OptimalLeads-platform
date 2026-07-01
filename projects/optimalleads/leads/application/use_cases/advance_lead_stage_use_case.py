from __future__ import annotations

import logging
from uuid import uuid4

from core_domain import EventEnvelope, Repository
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadStageChanged, LeadId, LeadStage

logger = logging.getLogger(__name__)


class AdvanceLeadStageUseCase:
    def __init__(self, repository: Repository[Lead, LeadId], outbox: LeadsOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, lead_id: str, stage: str, correlation_id: str | None = None) -> Lead:
        lead = await self._repository.get(lead_id)
        if lead is None:
            raise KeyError(lead_id)

        lead.change_stage(LeadStage.create(stage))
        await self._repository.save(lead)
        event = LeadStageChanged(lead_id=lead.id, stage=lead.stage)
        correlation_id = correlation_id or lead_id
        logger.info("leads.stage_changed", extra={"lead_id": lead_id, "correlation_id": correlation_id, "stage": stage})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=lead_id,
                event_name="LeadStageChanged",
                correlation_id=correlation_id,
                causation_id=None,
                payload={"lead_id": str(event.lead_id.value), "stage": event.stage.value},
            )
        )
        return lead
