from __future__ import annotations

import logging
from typing import Protocol

from core_domain import EventEnvelope

logger = logging.getLogger(__name__)


class SagaStateRepository(Protocol):
    async def has_processed(self, event_id: str) -> bool: ...

    async def mark_processed(self, event: EventEnvelope) -> None: ...


class OptimalLeadsSaga:
    def __init__(self, leads_client, analytics_client, state_repository: SagaStateRepository | None = None) -> None:
        self._leads_client = leads_client
        self._analytics_client = analytics_client
        self._state_repository = state_repository
        self._processed_event_ids: set[str] = set()

    async def handle(self, event: EventEnvelope) -> None:
        if await self._has_processed(event):
            logger.info("saga.event.duplicate", extra={"event_id": event.event_id, "event_name": event.event_name})
            return

        logger.info(
            "saga.event.received",
            extra={
                "event_id": event.event_id,
                "event_name": event.event_name,
                "aggregate_id": event.aggregate_id,
                "correlation_id": event.correlation_id,
            },
        )

        if event.event_name == "ConversationCreated":
            await self._handle_conversation_created(event)
        elif event.event_name in {"LeadCreated", "LeadStageChanged"}:
            await self._ingest_analytics(event)
        else:
            logger.debug("saga.event.ignored", extra={"event_name": event.event_name})

        await self._mark_processed(event)

    async def _has_processed(self, event: EventEnvelope) -> bool:
        if event.event_id in self._processed_event_ids:
            return True
        if self._state_repository is None:
            return False
        return await self._state_repository.has_processed(event.event_id)

    async def _mark_processed(self, event: EventEnvelope) -> None:
        self._processed_event_ids.add(event.event_id)
        if self._state_repository is not None:
            await self._state_repository.mark_processed(event)

    async def _handle_conversation_created(self, event: EventEnvelope) -> None:
        await self._ingest_analytics(event)

        title = str(event.payload.get("title") or event.payload.get("conversation_id") or event.aggregate_id)
        await self._leads_client.create_lead_from_conversation(
            conversation_id=str(event.payload.get("conversation_id") or event.aggregate_id),
            title=title,
            correlation_id=event.correlation_id,
        )

    async def _ingest_analytics(self, event: EventEnvelope) -> None:
        await self._analytics_client.ingest_event(event)