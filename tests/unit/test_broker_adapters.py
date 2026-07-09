from __future__ import annotations

from dataclasses import dataclass

import pytest

from core_domain import EventEnvelope, EventKind
from core_infrastructure.brokers.broker_factory import create_broker
from core_infrastructure.brokers.faststream_kafka import FastStreamKafkaBroker
from core_infrastructure.brokers.faststream_rabbitmq import FastStreamRabbitBroker


@dataclass(slots=True)
class BrokerSettings:
    broker_provider: str
    broker_url: str = "localhost:9092"
    broker_topic: str = "events"
    broker_queue: str = "events"
    broker_consumer_group: str = "test-group"


class FakeFastStreamBroker:
    def __init__(self, url: str) -> None:
        self.url = url
        self.published: list[dict[str, object]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def publish(self, **kwargs) -> None:
        self.published.append(kwargs)


def make_event() -> EventEnvelope:
    return EventEnvelope(
        event_id="event-1",
        aggregate_id="aggregate-1",
        event_name="ConversationCreated",
        event_kind=EventKind.DOMAIN,
        correlation_id="correlation-1",
        causation_id=None,
        occurred_at=None,
        payload={"conversation_id": "conversation-1"},
    )


@pytest.mark.asyncio
async def test_in_memory_broker_keeps_published_events() -> None:
    broker = create_broker(BrokerSettings(broker_provider="in_memory"))
    event = make_event()

    await broker.publish(event)

    assert broker.published == [event]


@pytest.mark.asyncio
async def test_kafka_broker_publishes_to_configured_topic(monkeypatch) -> None:
    from core_infrastructure.brokers import faststream_kafka

    monkeypatch.setattr(faststream_kafka, "KafkaBroker", FakeFastStreamBroker)
    broker = FastStreamKafkaBroker(BrokerSettings(broker_provider="faststream_kafka", broker_topic="chat-events"))
    event = make_event()

    await broker.publish(event)

    assert broker._broker.url == "localhost:9092"
    assert broker._broker.published == [
        {"message": event.model_dump(), "topic": "chat-events"},
    ]


@pytest.mark.asyncio
async def test_rabbitmq_broker_publishes_to_configured_queue(monkeypatch) -> None:
    from core_infrastructure.brokers import faststream_rabbitmq

    monkeypatch.setattr(faststream_rabbitmq, "RabbitBroker", FakeFastStreamBroker)
    broker = FastStreamRabbitBroker(BrokerSettings(broker_provider="faststream_rabbitmq", broker_queue="lead-events"))
    event = make_event()

    await broker.publish(event)

    assert broker._broker.url == "localhost:9092"
    assert broker._broker.published == [
        {"message": event.model_dump(), "queue": "lead-events"},
    ]