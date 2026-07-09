from __future__ import annotations

from core_infrastructure.brokers.broker_factory import BrokerFactory, create_broker

try:
	from core_infrastructure.brokers import in_memory  # noqa: F401
except ModuleNotFoundError:
	in_memory = None

try:
	from core_infrastructure.brokers import faststream_kafka  # noqa: F401
except ModuleNotFoundError:
	faststream_kafka = None

try:
	from core_infrastructure.brokers import faststream_rabbitmq  # noqa: F401
except ModuleNotFoundError:
	faststream_rabbitmq = None

try:
	from core_infrastructure.brokers import faststream_azure_service_bus  # noqa: F401
except ModuleNotFoundError:
	faststream_azure_service_bus = None

__all__ = ["BrokerFactory", "create_broker"]
