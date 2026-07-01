from __future__ import annotations

import logging

from core_domain.messaging import OutboxPort
from core_infrastructure.services.event_dispatcher import EventDispatcher


logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, outbox: OutboxPort, dispatcher: EventDispatcher) -> None:
        self._outbox = outbox
        self._dispatcher = dispatcher

    async def flush(self) -> int:
        events = await self._outbox.drain()
        published = 0

        for event in events:
            logger.info(
                "outbox.publish",
                extra={"event_name": event.event_name, "aggregate_id": event.aggregate_id, "correlation_id": event.correlation_id},
            )
            if await self._dispatcher.dispatch(event):
                published += 1

        return published