from __future__ import annotations

from .dead_letter import KafkaDeadLetterPublisher, RabbitDeadLetterPublisher
from .plans import SagaBridgeRuntime
from .proxies import KafkaBrokerProxy, RabbitBrokerProxy
from .retry.policy import FixedRetryPolicy
from .retry.config import BaseRetrySettings
from .protocols import BrokerFactory


class DefaultBrokerFactory:
    def build_chat_broker(self, broker_url: str):
        from faststream.kafka import KafkaBroker

        return KafkaBrokerProxy(KafkaBroker(broker_url))

    def build_leads_broker(self, broker_url: str):
        from faststream.rabbit import RabbitBroker

        return RabbitBrokerProxy(RabbitBroker(broker_url))


def build_saga_bridge_runtime(
    *,
    chat_broker_url: str,
    leads_broker_url: str,
    chat_dead_letter_topic: str,
    leads_dead_letter_queue: str,
    chat_retry_settings: BaseRetrySettings,
    leads_retry_settings: BaseRetrySettings,
    broker_factory: BrokerFactory | None = None,
) -> SagaBridgeRuntime:
    factory = broker_factory or DefaultBrokerFactory()
    chat_broker = factory.build_chat_broker(chat_broker_url)
    leads_broker = factory.build_leads_broker(leads_broker_url)
    return SagaBridgeRuntime(
        chat_broker=chat_broker,
        leads_broker=leads_broker,
        chat_retry_policy=FixedRetryPolicy(chat_retry_settings),
        leads_retry_policy=FixedRetryPolicy(leads_retry_settings),
        chat_dead_letter_publisher=KafkaDeadLetterPublisher(
            target_name="chat_inbound",
            broker=chat_broker,
            topic=chat_dead_letter_topic,
        ),
        leads_dead_letter_publisher=RabbitDeadLetterPublisher(
            target_name="leads_inbound",
            broker=leads_broker,
            queue=leads_dead_letter_queue,
        ),
    )
