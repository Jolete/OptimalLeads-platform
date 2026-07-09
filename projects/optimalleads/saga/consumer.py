from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from core_domain import EventEnvelope
from faststream.kafka import KafkaBroker
from faststream.rabbit import RabbitBroker
from projects.optimalleads.chat.settings import get_settings as get_chat_settings
from projects.optimalleads.leads.settings import get_settings as get_leads_settings
from projects.optimalleads.saga.clients import build_analytics_client, build_leads_client
from projects.optimalleads.saga.persistence import build_saga_state_repository
from projects.optimalleads.saga.process_manager import OptimalLeadsSaga
from projects.optimalleads.saga.settings import get_settings as get_saga_settings

logger = logging.getLogger(__name__)


def decode_event(message: Any) -> EventEnvelope:
    if isinstance(message, EventEnvelope):
        return message
    if isinstance(message, bytes):
        return EventEnvelope.model_validate(json.loads(message.decode("utf-8")))
    if isinstance(message, str):
        return EventEnvelope.model_validate(json.loads(message))
    return EventEnvelope.model_validate(message)


class OptimalLeadsSagaConsumer:
    def __init__(self, kafka_broker: KafkaBroker, rabbit_broker: RabbitBroker) -> None:
        self._kafka_broker = kafka_broker
        self._rabbit_broker = rabbit_broker

    async def run_forever(self) -> None:
        await self._kafka_broker.start()
        await self._rabbit_broker.start()
        logger.info("saga.consumer.started")
        try:
            await asyncio.Event().wait()
        finally:
            await self._rabbit_broker.close()
            await self._kafka_broker.close()


async def build_saga_consumer() -> OptimalLeadsSagaConsumer:
    chat_settings = get_chat_settings()
    leads_settings = get_leads_settings()
    saga_settings = get_saga_settings()
    state_repository = await build_saga_state_repository(saga_settings.saga_database_url)

    saga = OptimalLeadsSaga(
        leads_client=build_leads_client(saga_settings),
        analytics_client=build_analytics_client(saga_settings),
        state_repository=state_repository,
    )

    kafka_broker = KafkaBroker(chat_settings.broker_url)
    rabbit_broker = RabbitBroker(leads_settings.broker_url)

    @kafka_broker.subscriber(
        chat_settings.broker_topic,
        group_id="optimalleads-saga-chat-group",
        auto_offset_reset="earliest",
    )
    async def consume_chat_event(message: Any) -> None:
        event = decode_event(message)
        logger.info("saga.kafka.event", extra={"topic": chat_settings.broker_topic, "event_name": event.event_name})
        await saga.handle(event)

    @rabbit_broker.subscriber(leads_settings.broker_queue)
    async def consume_leads_event(message: Any) -> None:
        event = decode_event(message)
        logger.info("saga.rabbit.event", extra={"queue": leads_settings.broker_queue, "event_name": event.event_name})
        await saga.handle(event)

    return OptimalLeadsSagaConsumer(kafka_broker, rabbit_broker)