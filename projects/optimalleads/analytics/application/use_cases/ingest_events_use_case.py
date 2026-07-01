from __future__ import annotations

import logging

from core_domain import EventEnvelope
from projects.optimalleads.analytics.application.ports import AnalyticsStorePort

logger = logging.getLogger(__name__)


class IngestEventsUseCase:
    def __init__(self, store: AnalyticsStorePort) -> None:
        self._store = store

    async def execute(self, event: EventEnvelope) -> None:
        logger.info(
            "analytics.ingest",
            extra={
                "event_name": event.event_name,
                "aggregate_id": event.aggregate_id,
                "correlation_id": event.correlation_id,
            },
        )
        snapshot = await self._store.get_snapshot()

        if event.event_name == "ConversationCreated":
            snapshot.register_conversation(str(event.payload["conversation_id"]), str(event.payload["title"]))
        elif event.event_name == "ConversationMessageAppended":
            snapshot.append_conversation_message(str(event.payload["conversation_id"]))
        elif event.event_name == "LeadCreated":
            snapshot.register_lead(str(event.payload["lead_id"]), str(event.payload["name"]))
        elif event.event_name == "LeadStageChanged":
            snapshot.change_lead_stage(str(event.payload["lead_id"]), str(event.payload["stage"]))

        await self._store.upsert_snapshot(snapshot)
