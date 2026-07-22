from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from core_domain import EventEnvelope
from projects.optimalleads.chat.settings import get_settings as get_chat_settings
from projects.optimalleads.leads.settings import get_settings as get_leads_settings
from projects.optimalleads.saga.bridge import SagaBridge, SagaBridgeContract, SagaBridgeResponsibilities, SagaBridgeRoutePlan, SagaBridgeTopology, build_saga_bridge_runtime, create_saga_bridge
from projects.optimalleads.saga.clients import build_analytics_client, build_leads_client
from projects.optimalleads.saga.infrastructure.persistence.bootstrap import build_saga_state_repository
from projects.optimalleads.saga.process_manager import OptimalLeadsSaga
from projects.optimalleads.saga.settings import get_settings as get_saga_settings
from projects.optimalleads.saga.infrastructure.persistence.settings import get_persistence_settings

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
    def __init__(self, bridge: SagaBridge) -> None:
        self._bridge = bridge

    async def run_forever(self) -> None:
        await self._bridge.start()
        logger.info("saga.consumer.started")
        try:
            await asyncio.Event().wait()
        finally:
            await self._bridge.stop()


async def build_saga_consumer() -> OptimalLeadsSagaConsumer:
    chat_settings = get_chat_settings()
    leads_settings = get_leads_settings()
    saga_settings = get_saga_settings()
    persistence_settings = get_persistence_settings()
    state_repository = await build_saga_state_repository(
        persistence_settings.business_database_url,
        persistence_settings.reset_database_on_startup,
    )

    saga = OptimalLeadsSaga(
        leads_client=build_leads_client(saga_settings),
        analytics_client=build_analytics_client(saga_settings),
        state_repository=state_repository,
    )

    chat_retry_settings = saga_settings.saga_bridge_chat_retry_settings
    leads_retry_settings = saga_settings.saga_bridge_leads_retry_settings

    topology = SagaBridgeTopology(
        chat_broker_url=chat_settings.broker_url,
        chat_broker_topic=saga_settings.chat_broker_topic,
        chat_consumer_group=saga_settings.chat_consumer_group,
        leads_broker_url=leads_settings.broker_url,
        leads_broker_queue=saga_settings.leads_broker_queue,
        leads_consumer_group=saga_settings.leads_consumer_group,
        replay_topic=saga_settings.saga_bridge_replay_topic,
        chat_retry_topic=saga_settings.saga_bridge_chat_retry_topic,
        leads_retry_queue=saga_settings.saga_bridge_leads_retry_queue,
        chat_dead_letter_topic=saga_settings.chat_dead_letter_topic,
        leads_dead_letter_queue=saga_settings.leads_dead_letter_queue,
        enabled=saga_settings.saga_bridge_enabled,
        route_chat_to_leads=saga_settings.saga_bridge_route_chat_to_leads,
        route_events_to_analytics=saga_settings.saga_bridge_route_events_to_analytics,
    )

    contract = SagaBridgeContract(
        inbound_chat=SagaBridgeRoutePlan(
            name="chat_inbound",
            enabled=saga_settings.saga_bridge_route_chat_to_leads,
            consumer_group=saga_settings.chat_consumer_group,
            retry_topic=saga_settings.saga_bridge_chat_retry_topic,
            dead_letter_target=saga_settings.chat_dead_letter_topic,
            retry_settings=chat_retry_settings,
        ),
        inbound_leads=SagaBridgeRoutePlan(
            name="leads_inbound",
            enabled=saga_settings.saga_bridge_route_events_to_analytics,
            consumer_group=saga_settings.leads_consumer_group,
            retry_topic=saga_settings.saga_bridge_leads_retry_queue,
            dead_letter_target=saga_settings.leads_dead_letter_queue,
            retry_settings=leads_retry_settings,
        ),
    )

    runtime = build_saga_bridge_runtime(
        chat_broker_url=topology.chat_broker_url,
        leads_broker_url=topology.leads_broker_url,
        chat_dead_letter_topic=topology.chat_dead_letter_topic,
        leads_dead_letter_queue=topology.leads_dead_letter_queue,
        chat_retry_settings=chat_retry_settings,
        leads_retry_settings=leads_retry_settings,
    )

    bridge = create_saga_bridge(
        topology=topology,
        contract=contract,
        chat_broker=runtime.chat_broker,
        leads_broker=runtime.leads_broker,
        chat_dead_letter_publisher=runtime.chat_dead_letter_publisher,
        leads_dead_letter_publisher=runtime.leads_dead_letter_publisher,
        responsibilities=SagaBridgeResponsibilities(
            decode_event=decode_event,
            route_chat_event=saga.handle,
            route_leads_event=saga.handle,
            chat_retry_policy=runtime.chat_retry_policy,
            leads_retry_policy=runtime.leads_retry_policy,
        ),
    )

    return OptimalLeadsSagaConsumer(bridge)