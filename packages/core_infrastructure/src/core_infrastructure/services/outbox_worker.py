from __future__ import annotations

import logging

from core_domain.messaging import OutboxPort
from opentelemetry import trace
from core_infrastructure.services.event_dispatcher import EventDispatcher


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class OutboxWorker:
    def __init__(self, outbox: OutboxPort, dispatcher: EventDispatcher) -> None:
        self._outbox = outbox
        self._dispatcher = dispatcher

    async def flush(self) -> int:
        events = await self._outbox.drain()
        published = 0

        for event in events:
            with tracer.start_as_current_span(f"outbox.publish.{event.event_name}") as span:
                span.set_attribute("event.name", event.event_name)
                span.set_attribute("event.aggregate_id", event.aggregate_id)
                span.set_attribute("event.correlation_id", event.correlation_id)
                logger.info(
                    "outbox.publish",
                    extra={"event_name": event.event_name, "aggregate_id": event.aggregate_id, "correlation_id": event.correlation_id},
                )
                if await self._dispatcher.dispatch(event):
                    published += 1

        return published