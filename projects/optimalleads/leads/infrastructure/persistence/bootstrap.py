from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from core_domain.messaging import CqrsMediator
from core_infrastructure.composition_root.persistence_composition import build_broker, build_dispatcher
from core_infrastructure.drivers.sqlserver import bootstrap_sqlserver_database  # noqa: F401
from core_infrastructure.services import OutboxWorker
from projects.optimalleads.leads.application.dto import AdvanceLeadStageCommand, CreateLeadCommand, DeleteLeadCommand, GetLeadQuery, ListLeadsQuery, UpdateLeadCommand
from projects.optimalleads.leads.application.handlers import AdvanceLeadStageHandler, CreateLeadHandler, DeleteLeadHandler, GetLeadHandler, ListLeadsHandler, UpdateLeadHandler
from projects.optimalleads.leads.application.use_cases import AdvanceLeadStageUseCase, CreateLeadUseCase, DeleteLeadUseCase, GetLeadUseCase, ListLeadsUseCase, UpdateLeadUseCase
from projects.optimalleads.leads.infrastructure.persistence.factory import build_leads_memory_runtime, build_leads_outbox_factory, build_leads_repository_factory
from projects.optimalleads.leads.infrastructure.persistence.database import create_leads_engine, create_leads_session_factory
from projects.optimalleads.leads.infrastructure.persistence.memory import MemoryLeadRepository, MemoryLeadsOutbox
from projects.optimalleads.leads.infrastructure.persistence.settings import get_persistence_settings
from core_infrastructure.persistence.persistence_factory import create_database_bootstrap
from projects.optimalleads.leads.settings import get_settings


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LeadsRuntime:
    business_database_url: str
    outbox_database_url: str
    audit_database_url: str
    events_database_url: str
    repository: object
    uow_factory: Callable[[], object] | None
    mediator: CqrsMediator | None
    outbox: object
    outbox_worker: OutboxWorker | None


_runtime: LeadsRuntime | None = None


async def get_leads_runtime() -> LeadsRuntime:
    global _runtime

    if _runtime is not None:
        logger.debug("leads.runtime.cached", extra={"runtime_type": type(_runtime).__name__})
        return _runtime

    settings = get_persistence_settings()
    logger.info(
        "leads.runtime.building",
        extra={"provider": settings.persistence_provider, "reset_database_on_startup": settings.reset_database_on_startup},
    )

    if settings.persistence_provider == "memory":
        logger.debug("leads.runtime.memory.bootstrap.begin")
        repository_factory, outbox = build_leads_memory_runtime()
        repository = repository_factory()
        mediator = CqrsMediator(None)
        mediator.register_handler(CreateLeadCommand, CreateLeadHandler(CreateLeadUseCase(repository, outbox)))
        mediator.register_handler(UpdateLeadCommand, UpdateLeadHandler(UpdateLeadUseCase(repository, outbox)))
        mediator.register_handler(AdvanceLeadStageCommand, AdvanceLeadStageHandler(AdvanceLeadStageUseCase(repository, outbox)))
        mediator.register_handler(DeleteLeadCommand, DeleteLeadHandler(DeleteLeadUseCase(repository, outbox)))
        mediator.register_handler(GetLeadQuery, GetLeadHandler(GetLeadUseCase(repository)))
        mediator.register_handler(ListLeadsQuery, ListLeadsHandler(ListLeadsUseCase(repository)))
        _runtime = LeadsRuntime(
            business_database_url=settings.business_database_url,
            outbox_database_url=settings.business_database_url,
            audit_database_url=settings.business_database_url,
            events_database_url=settings.business_database_url,
            repository=repository_factory(),
            uow_factory=None,
            mediator=mediator,
            outbox=outbox,
            outbox_worker=None,
        )
        logger.info(
            "leads.runtime.memory.ready",
            extra={
                "repository_type": type(repository).__name__,
                "mediator_type": type(mediator).__name__,
            },
        )
        return _runtime

    logger.debug("leads.runtime.sql.bootstrap.begin", extra={"business_database_url": settings.business_database_url})
    business_engine = create_leads_engine(settings.business_database_url)
    bootstrap_database = create_database_bootstrap(settings.persistence_provider)
    await bootstrap_database(
        settings.business_database_url,
        "projects/optimalleads/leads/infrastructure/persistence/alembic",
        settings.reset_database_on_startup,
    )
    logger.info("leads.runtime.database.bootstrap.completed")

    business_session_factory = create_leads_session_factory(business_engine)
    outbox = build_leads_outbox_factory(business_session_factory())
    app_settings = get_settings()
    broker = build_broker(app_settings)
    dispatcher = build_dispatcher(broker)
    outbox_worker = OutboxWorker(outbox, dispatcher)
    repository_factory = build_leads_repository_factory(business_session_factory)
    repository = repository_factory()
    mediator = CqrsMediator(None)
    logger.debug("leads.runtime.handlers.registering")
    mediator.register_handler(CreateLeadCommand, CreateLeadHandler(CreateLeadUseCase(repository, outbox)))
    mediator.register_handler(UpdateLeadCommand, UpdateLeadHandler(UpdateLeadUseCase(repository, outbox)))
    mediator.register_handler(AdvanceLeadStageCommand, AdvanceLeadStageHandler(AdvanceLeadStageUseCase(repository, outbox)))
    mediator.register_handler(DeleteLeadCommand, DeleteLeadHandler(DeleteLeadUseCase(repository, outbox)))
    mediator.register_handler(GetLeadQuery, GetLeadHandler(GetLeadUseCase(repository)))
    mediator.register_handler(ListLeadsQuery, ListLeadsHandler(ListLeadsUseCase(repository)))

    _runtime = LeadsRuntime(
        business_database_url=settings.business_database_url,
        outbox_database_url=settings.business_database_url,
        audit_database_url=settings.business_database_url,
        events_database_url=settings.business_database_url,
        repository=repository,
        uow_factory=None,
        mediator=mediator,
        outbox=outbox,
        outbox_worker=outbox_worker,
    )
    logger.info(
        "leads.runtime.sql.ready",
        extra={
            "repository_type": type(repository).__name__,
            "mediator_type": type(mediator).__name__,
            "outbox_worker_type": type(outbox_worker).__name__,
        },
    )
    return _runtime
