from __future__ import annotations

import logging
from uuid import uuid4

from core_domain import EventEnvelope, Repository
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadId, LeadName, LeadStage

logger = logging.getLogger(__name__)


class UpdateLeadUseCase:
    def __init__(self, repository: Repository[Lead, LeadId], outbox: LeadsOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, lead_id: str, name: str, stage: str | None = None, correlation_id: str | None = None) -> Lead:
        lead = await self._repository.get(lead_id)
        if lead is None:
            raise KeyError(lead_id)

        lead.name = LeadName.create(name)
        if stage is not None:
            lead.change_stage(LeadStage.create(stage))
        await self._repository.save(lead)
        correlation_id = correlation_id or lead_id
        logger.info("leads.updated", extra={"lead_id": lead_id, "correlation_id": correlation_id})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=lead_id,
                event_name="LeadUpdated",
                correlation_id=correlation_id,
                causation_id=None,
                payload={"lead_id": lead_id, "name": name, "stage": lead.stage.value},
            )
        )
        return lead
