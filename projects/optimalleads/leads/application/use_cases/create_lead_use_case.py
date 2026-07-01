from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadCreated, LeadId, LeadName

logger = logging.getLogger(__name__)


class CreateLeadUseCase:
    def __init__(self, repository: Repository[Lead, LeadId], outbox: LeadsOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, name: str, correlation_id: str | None = None) -> Lead:
        lead = Lead(id=LeadId.create_unique(), name=LeadName.create(name))
        await self._repository.add(lead)
        lead_id = str(lead.id.value)
        event = LeadCreated(lead_id=lead.id, name=lead.name)
        correlation_id = correlation_id or lead_id
        logger.info("leads.created", extra={"lead_id": lead_id, "correlation_id": correlation_id})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=lead_id,
                event_name="LeadCreated",
                event_kind=EventKind.DOMAIN,
                correlation_id=correlation_id,
                causation_id=None,
                occurred_at=datetime.now(timezone.utc).isoformat(),
                payload={"lead_id": str(event.lead_id.value), "name": event.name.value},
            )
        )
        return lead
