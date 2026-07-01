from __future__ import annotations

import logging

from core_domain.contracts import EventEnvelope
from core_domain.messaging import MessageBrokerPort


logger = logging.getLogger(__name__)


class InProcessMessageBroker(MessageBrokerPort):
    async def publish(self, event: EventEnvelope) -> None:
        logger.info(
            "chat.broker.publish",
            extra={
                "event_id": event.event_id,
                "event_name": event.event_name,
                "aggregate_id": event.aggregate_id,
                "correlation_id": event.correlation_id,
            },
        )
