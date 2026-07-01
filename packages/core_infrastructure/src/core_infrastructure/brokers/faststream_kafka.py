from __future__ import annotations

import logging

from faststream.kafka import KafkaBroker

from core_domain.contracts import EventEnvelope
from core_domain.messaging import MessageBrokerPort
from core_domain.broker_config import BrokerConfig
from core_infrastructure.brokers.broker_factory import register_broker


logger = logging.getLogger(__name__)


class FastStreamKafkaBroker(MessageBrokerPort):
    def __init__(self, settings: BrokerConfig) -> None:
        self._settings = settings
        self._broker = KafkaBroker(self._settings.broker_url)

    async def publish(self, event: EventEnvelope) -> None:
        logger.info(
            "broker.faststream.kafka.publish",
            extra={
                "broker_url": self._settings.broker_url,
                "topic": self._settings.broker_topic,
                "event_name": event.event_name,
                "aggregate_id": event.aggregate_id,
                "correlation_id": event.correlation_id,
            },
        )

        async with self._broker:
            await self._broker.publish(
                message=event.model_dump(),
                topic=self._settings.broker_topic,
            )


register_broker("faststream_kafka", lambda settings: FastStreamKafkaBroker(settings))
