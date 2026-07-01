from __future__ import annotations

from typing import Literal, Protocol


class BrokerConfig(Protocol):
    broker_provider: Literal["in_memory", "faststream_kafka", "faststream_rabbitmq", "faststream_azure_service_bus"]
    broker_url: str
    broker_topic: str
    broker_queue: str
    broker_consumer_group: str
