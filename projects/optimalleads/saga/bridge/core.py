from __future__ import annotations

import asyncio
import logging
from typing import Any

from core_domain import EventEnvelope

from .plans import SagaBridgeContract, SagaBridgeResponsibilities, SagaBridgeTopology
from .protocols import DeadLetterPublisher, SagaEventHandler
from .retry.protocols import RetryPolicy

logger = logging.getLogger(__name__)


class SagaBridge:
    def __init__(
        self,
        topology: SagaBridgeTopology,
        contract: SagaBridgeContract,
        chat_broker: Any,
        leads_broker: Any,
        responsibilities: SagaBridgeResponsibilities,
    ) -> None:
        self._topology = topology
        self._contract = contract
        self._chat_broker = chat_broker
        self._leads_broker = leads_broker
        self._responsibilities = responsibilities

    async def start(self) -> None:
        await self._chat_broker.start()
        await self._leads_broker.start()
        logger.info(
            "saga.bridge.started",
            extra={
                "enabled": self._topology.enabled,
                "chat_route": self._contract.inbound_chat.name,
                "leads_route": self._contract.inbound_leads.name,
                "chat_topic": self._topology.chat_broker_topic,
                "leads_queue": self._topology.leads_broker_queue,
            },
        )

    async def stop(self) -> None:
        await self._leads_broker.close()
        await self._chat_broker.close()

    def register(self) -> None:
        @self._chat_broker.subscriber(
            self._topology.chat_broker_topic,
            group_id=self._topology.chat_consumer_group,
            auto_offset_reset="earliest",
        )
        async def consume_chat_event(message: Any) -> None:
            event = self._responsibilities.decode_event(message)
            logger.info("saga.bridge.chat.event", extra={"topic": self._topology.chat_broker_topic, "event_name": event.event_name})
            if self._contract.inbound_chat.enabled:
                await self._route_event(
                    event,
                    self._responsibilities.route_chat_event,
                    self._responsibilities.chat_retry_policy,
                    self._responsibilities.chat_dead_letter_publisher,
                )
            else:
                logger.debug("saga.bridge.chat.route.disabled", extra={"event_name": event.event_name})

        @self._leads_broker.subscriber(self._topology.leads_broker_queue)
        async def consume_leads_event(message: Any) -> None:
            event = self._responsibilities.decode_event(message)
            logger.info("saga.bridge.leads.event", extra={"queue": self._topology.leads_broker_queue, "event_name": event.event_name})
            if self._contract.inbound_leads.enabled:
                await self._route_event(
                    event,
                    self._responsibilities.route_leads_event,
                    self._responsibilities.leads_retry_policy,
                    self._responsibilities.leads_dead_letter_publisher,
                )
            else:
                logger.debug("saga.bridge.leads.route.disabled", extra={"event_name": event.event_name})

    async def _route_event(
        self,
        event: EventEnvelope,
        handler: SagaEventHandler,
        retry_policy: RetryPolicy | None,
        dead_letter_publisher: DeadLetterPublisher | None,
    ) -> None:
        last_error: Exception | None = None
        attempt = 1

        while True:
            try:
                await handler(event)
                return
            except Exception as error:
                last_error = error
                logger.exception(
                    "saga.bridge.route.failed",
                    extra={
                        "event_name": event.event_name,
                        "event_id": event.event_id,
                        "attempt": attempt,
                        "max_attempts": getattr(retry_policy, "max_attempts", 1) if retry_policy is not None else 1,
                    },
                )
                if retry_policy is None or not retry_policy.should_retry(attempt):
                    break
                delay = retry_policy.next_delay_seconds(attempt)
                logger.warning(
                    "saga.bridge.retry.scheduled",
                    extra={"event_id": event.event_id, "attempt": attempt, "delay_seconds": delay},
                )
                await asyncio.sleep(delay)
                attempt += 1

        if dead_letter_publisher is not None and last_error is not None:
            await dead_letter_publisher.publish(event, reason=str(last_error))
        if last_error is not None:
            raise last_error


class FixedRetryPolicy:
    def __init__(self, settings) -> None:
        self._settings = settings

    @property
    def max_attempts(self) -> int:
        return self._settings.max_attempts

    def should_retry(self, attempt: int) -> bool:
        return attempt < self._settings.max_attempts

    def next_delay_seconds(self, attempt: int) -> float:
        return float(self._settings.backoff_seconds * attempt)


def create_saga_bridge(
    *,
    topology: SagaBridgeTopology,
    contract: SagaBridgeContract,
    chat_broker: Any,
    leads_broker: Any,
    chat_dead_letter_publisher: DeadLetterPublisher | None,
    leads_dead_letter_publisher: DeadLetterPublisher | None,
    responsibilities: SagaBridgeResponsibilities,
) -> SagaBridge:
    bridge = SagaBridge(
        topology,
        contract,
        chat_broker,
        leads_broker,
        SagaBridgeResponsibilities(
            decode_event=responsibilities.decode_event,
            route_chat_event=responsibilities.route_chat_event,
            route_leads_event=responsibilities.route_leads_event,
            chat_retry_policy=responsibilities.chat_retry_policy,
            leads_retry_policy=responsibilities.leads_retry_policy,
            chat_dead_letter_publisher=chat_dead_letter_publisher,
            leads_dead_letter_publisher=leads_dead_letter_publisher,
        ),
    )
    bridge.register()
    return bridge
