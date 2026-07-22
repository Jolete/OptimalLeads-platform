from __future__ import annotations

import logging
from typing import Any

from core_domain import EventEnvelope

from .protocols import DeadLetterPublisher

logger = logging.getLogger(__name__)


class BrokerDeadLetterPublisher:
    def __init__(self, target_name: str, broker: Any, target_kind: str, target_value: str) -> None:
        self._target_name = target_name
        self._broker = broker
        self._target_kind = target_kind
        self._target_value = target_value

    async def publish(self, event: EventEnvelope, reason: str) -> None:
        dead_letter_event = event.model_copy(
            update={
                "event_name": f"{event.event_name}.dead_letter",
                "event_kind": event.event_kind,
                "payload": {
                    **event.payload,
                    "dead_letter_reason": reason,
                    "dead_letter_source": self._target_name,
                },
            }
        )
        async with self._broker:
            await self._broker.publish(
                message=dead_letter_event.model_dump(),
                **{self._target_kind: self._target_value},
            )
        logger.error(
            "saga.bridge.dead_letter",
            extra={
                "target_name": self._target_name,
                "event_id": event.event_id,
                "event_name": event.event_name,
                "correlation_id": event.correlation_id,
                "reason": reason,
            },
        )


class KafkaDeadLetterPublisher(BrokerDeadLetterPublisher):
    def __init__(self, target_name: str, broker: Any, topic: str) -> None:
        super().__init__(target_name=target_name, broker=broker, target_kind="topic", target_value=topic)


class RabbitDeadLetterPublisher(BrokerDeadLetterPublisher):
    def __init__(self, target_name: str, broker: Any, queue: str) -> None:
        super().__init__(target_name=target_name, broker=broker, target_kind="queue", target_value=queue)
