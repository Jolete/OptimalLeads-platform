from __future__ import annotations

import logging

from core_domain.contracts import EventEnvelope
from core_domain.messaging import MessageBrokerPort
from core_infrastructure.brokers.broker_factory import register_broker


logger = logging.getLogger(__name__)


class InMemoryBroker(MessageBrokerPort):
    def __init__(self) -> None:
        self.published: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        self.published.append(event)
        logger.info("broker.in_memory.publish", extra={"event_name": event.event_name, "aggregate_id": event.aggregate_id, "correlation_id": event.correlation_id})


register_broker("in_memory", lambda settings: InMemoryBroker())
