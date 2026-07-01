from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from core_infrastructure.brokers import create_broker
from core_infrastructure.services import OutboxWorker, create_broker_dispatcher

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


@dataclass(slots=True)
class GenericPersistenceRuntime:
    repository_factory: Callable[[], object] | None
    uow_factory: Callable[[], object] | None
    outbox: object | None
    outbox_worker: OutboxWorker | None


@dataclass(slots=True)
class PersistenceWiring:
    repository_factory: Callable[[], object] | None = None
    uow_factory: Callable[[], object] | None = None
    outbox_factory: Callable[[], object] | None = None
    outbox_worker_factory: Callable[[object, object], OutboxWorker] | None = None
    memory_runtime_factory: Callable[[], tuple[Callable[[], object] | None, object | None]] | None = None


def build_broker(settings: Any) -> Any:
    broker = create_broker(settings)
    return broker


def build_dispatcher(broker: Any) -> Any:
    return create_broker_dispatcher(broker)


def build_memory_runtime(memory_runtime_factory: Callable[[], tuple[Callable[[], object] | None, object | None]]) -> GenericPersistenceRuntime:
    repository_factory, outbox = memory_runtime_factory()
    return GenericPersistenceRuntime(
        repository_factory=repository_factory,
        uow_factory=None,
        outbox=outbox,
        outbox_worker=None,
    )
