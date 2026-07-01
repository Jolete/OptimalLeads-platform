from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from core_domain.messaging import CqrsMediator
from core_infrastructure.composition_root.persistence_composition import build_broker, build_dispatcher
from projects.optimalleads.analytics.infrastructure.persistence.factory import build_analytics_memory_store
from projects.optimalleads.analytics.application.dto import IngestEventCommand, ReadSnapshotQuery
from projects.optimalleads.analytics.application.handlers import IngestEventHandler, ReadSnapshotHandler
from projects.optimalleads.analytics.application.use_cases import IngestEventsUseCase, ReadSnapshotUseCase
from projects.optimalleads.analytics.infrastructure.persistence.database import create_analytics_engine, create_analytics_session_factory
from projects.optimalleads.analytics.infrastructure.persistence.store import AnalyticsSnapshotStore
from projects.optimalleads.analytics.infrastructure.persistence.settings import get_persistence_settings
from core_infrastructure.persistence.persistence_factory import create_database_bootstrap
from core_infrastructure.drivers.sqlserver.database_composition import bootstrap_sqlserver_database
from core_infrastructure.services import OutboxWorker
from projects.optimalleads.analytics.infrastructure.services.outbox_worker import AnalyticsOutboxWorker
from projects.optimalleads.analytics.settings import get_settings


@dataclass(slots=True)
class AnalyticsRuntime:
    business_database_url: str
    outbox_database_url: str
    audit_database_url: str
    events_database_url: str
    store_factory: Callable[[], object]
    mediator: CqrsMediator | None
    outbox_worker: OutboxWorker | None


_runtime: AnalyticsRuntime | None = None


async def get_analytics_runtime() -> AnalyticsRuntime:
    global _runtime

    if _runtime is not None:
        return _runtime

    settings = get_persistence_settings()

    if settings.persistence_provider == "memory":
        store = build_analytics_memory_store()
        mediator = CqrsMediator(None)
        mediator.register_handler(IngestEventCommand, IngestEventHandler(IngestEventsUseCase(store)))
        mediator.register_handler(ReadSnapshotQuery, ReadSnapshotHandler(ReadSnapshotUseCase(store)))
        _runtime = AnalyticsRuntime(
            business_database_url=settings.business_database_url,
            outbox_database_url=settings.business_database_url,
            audit_database_url=settings.business_database_url,
            events_database_url=settings.business_database_url,
            store_factory=lambda session: store,
            mediator=mediator,
            outbox_worker=None,
        )
        return _runtime

    _ = bootstrap_sqlserver_database
    bootstrap_database = create_database_bootstrap(settings.persistence_provider)
    await bootstrap_database(
        settings.business_database_url,
        "projects/optimalleads/analytics/infrastructure/persistence/alembic",
        settings.reset_database_on_startup,
    )

    session_factory = create_analytics_session_factory(create_analytics_engine(settings.business_database_url))
    store = AnalyticsSnapshotStore(session_factory())
    mediator = CqrsMediator(None)
    mediator.register_handler(IngestEventCommand, IngestEventHandler(IngestEventsUseCase(store)))
    mediator.register_handler(ReadSnapshotQuery, ReadSnapshotHandler(ReadSnapshotUseCase(store)))

    app_settings = get_settings()
    broker = build_broker(app_settings)
    dispatcher = build_dispatcher(broker)
    outbox_worker = AnalyticsOutboxWorker(store, dispatcher)

    _runtime = AnalyticsRuntime(
        business_database_url=settings.business_database_url,
        outbox_database_url=settings.business_database_url,
        audit_database_url=settings.business_database_url,
        events_database_url=settings.business_database_url,
        store_factory=lambda session: AnalyticsSnapshotStore(session),
        mediator=mediator,
        outbox_worker=outbox_worker,
    )
    return _runtime
