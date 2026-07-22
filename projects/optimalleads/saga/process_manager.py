from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from core_domain import EventEnvelope

logger = logging.getLogger(__name__)


class SagaStatus(StrEnum):
    RECEIVED = "received"
    ANALYTICS_INGESTED = "analytics_ingested"
    LEAD_REQUESTED = "lead_requested"
    LEAD_CREATED = "lead_created"
    FAILED = "failed"


@dataclass(slots=True)
class SagaProgress:
    event_id: str
    event_name: str
    correlation_id: str
    causation_id: str | None
    aggregate_id: str
    status: SagaStatus = SagaStatus.RECEIVED
    current_phase: str = "received"
    completed_steps: list[str] = field(default_factory=list)
    last_error: str | None = None


class SagaStateRepository(Protocol):
    async def has_processed(self, event_id: str) -> bool: ...

    async def mark_processed(self, event: EventEnvelope) -> None: ...

    async def load_progress(self, correlation_id: str) -> SagaProgress | None: ...

    async def save_progress(self, progress: SagaProgress) -> None: ...


class OptimalLeadsSaga:
    def __init__(self, leads_client, analytics_client, state_repository: SagaStateRepository | None = None) -> None:
        self._leads_client = leads_client
        self._analytics_client = analytics_client
        self._state_repository = state_repository
        self._processed_event_ids: set[str] = set()

    async def handle(self, event: EventEnvelope) -> None:
        logger.info(
            "saga.handle.enter",
            extra={
                "event_id": event.event_id,
                "event_name": event.event_name,
                "aggregate_id": event.aggregate_id,
                "correlation_id": event.correlation_id,
                "causation_id": event.causation_id,
            },
        )
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
                "causation_id": event.causation_id,
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
        logger.info(
            "saga.conversation_created.enter",
            extra={
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
                "aggregate_id": event.aggregate_id,
            },
        )
        await self._save_progress(event, SagaStatus.RECEIVED, "conversation-created:received")
        await self._ingest_analytics(event)
        logger.info(
            "saga.conversation_created.analytics_ingested",
            extra={
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
            },
        )
        await self._save_progress(event, SagaStatus.ANALYTICS_INGESTED, "conversation-created:analytics-ingested")

        title = str(event.payload.get("title") or event.payload.get("conversation_id") or event.aggregate_id)
        try:
            await self._save_progress(event, SagaStatus.LEAD_REQUESTED, "conversation-created:lead-requested")
            logger.info(
                "saga.conversation_created.lead_request",
                extra={
                    "event_id": event.event_id,
                    "correlation_id": event.correlation_id,
                    "conversation_id": str(event.payload.get("conversation_id") or event.aggregate_id),
                    "title": title,
                },
            )
            await self._leads_client.create_lead_from_conversation(
                conversation_id=str(event.payload.get("conversation_id") or event.aggregate_id),
                title=title,
                correlation_id=event.correlation_id,
            )
        except Exception as error:
            logger.exception(
                "saga.conversation_created.lead_request_failed",
                extra={
                    "event_id": event.event_id,
                    "correlation_id": event.correlation_id,
                },
            )
            await self._save_progress(event, SagaStatus.FAILED, "conversation-created:lead-failed", str(error))
            raise
        logger.info(
            "saga.conversation_created.lead_created",
            extra={
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
            },
        )
        await self._save_progress(event, SagaStatus.LEAD_CREATED, "conversation-created:lead-created")

    async def _ingest_analytics(self, event: EventEnvelope) -> None:
        await self._analytics_client.ingest_event(event)

    async def _save_progress(self, event: EventEnvelope, status: SagaStatus, step: str, error: str | None = None) -> None:
        if self._state_repository is None:
            return

        progress = await self._state_repository.load_progress(event.correlation_id)
        if progress is None:
            progress = SagaProgress(
                event_id=event.event_id,
                event_name=event.event_name,
                correlation_id=event.correlation_id,
                causation_id=event.causation_id,
                aggregate_id=event.aggregate_id,
            )
        if step not in progress.completed_steps:
            progress.completed_steps.append(step)
        progress.status = status
        progress.current_phase = step
        progress.last_error = error
        await self._state_repository.save_progress(progress)