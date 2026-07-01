from __future__ import annotations

import logging
from uuid import uuid4

from core_domain import EventEnvelope, Repository
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadId

logger = logging.getLogger(__name__)


class DeleteLeadUseCase:
    def __init__(self, repository: Repository[Lead, LeadId], outbox: LeadsOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, lead_id: str, correlation_id: str | None = None) -> None:
        lead = await self._repository.get(lead_id)
        if lead is None:
            raise KeyError(lead_id)

        await self._repository.delete_by_id(lead_id)
        correlation_id = correlation_id or lead_id
        logger.info("leads.deleted", extra={"lead_id": lead_id, "correlation_id": correlation_id})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=lead_id,
                event_name="LeadDeleted",
                correlation_id=correlation_id,
                causation_id=None,
                payload={"lead_id": lead_id},
            )
        )
