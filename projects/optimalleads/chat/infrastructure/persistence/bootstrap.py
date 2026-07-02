from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core_domain.messaging import CqrsMediator
from core_infrastructure.composition_root.persistence_composition import build_broker, build_dispatcher
from core_infrastructure.drivers.sqlserver import bootstrap_sqlserver_database  # noqa: F401
from core_infrastructure.persistence.persistence_factory import create_database_bootstrap
from core_infrastructure.services import OutboxWorker
from projects.optimalleads.chat.application.dto import AppendMessageCommand, CreateConversationCommand, DeleteConversationCommand, GetConversationQuery, ListConversationsQuery
from projects.optimalleads.chat.application.handlers import AppendMessageHandler, CreateConversationHandler, DeleteConversationHandler, GetConversationHandler, ListConversationsHandler
from projects.optimalleads.chat.application.use_cases import AppendMessageUseCase, CreateConversationUseCase, DeleteConversationUseCase, GetConversationUseCase, ListConversationsUseCase
from projects.optimalleads.chat.infrastructure.persistence.database import create_chat_engine, create_chat_session_factory
from projects.optimalleads.chat.infrastructure.persistence.factory import build_chat_memory_runtime, build_chat_outbox_factory, build_chat_repository_factory, build_chat_uow_factory
from projects.optimalleads.chat.infrastructure.persistence.settings import get_persistence_settings
from projects.optimalleads.chat.infrastructure.persistence.models.outbox import ChatOutboxRow
from projects.optimalleads.chat.infrastructure.services.outbox_worker import ChatOutboxWorker
from projects.optimalleads.chat.settings import get_settings

import logging


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ChatRuntime:
    repository_factory: Callable[[], object]
    uow_factory: Callable[[], object] | None
    mediator: CqrsMediator | None
    outbox: object
    outbox_worker: OutboxWorker | None


_runtime: ChatRuntime | None = None


async def get_chat_runtime() -> ChatRuntime:
    global _runtime

    if _runtime is not None:
        return _runtime

    settings = get_persistence_settings()

    if settings.persistence_provider == "memory":
        repository_factory, outbox = build_chat_memory_runtime()
        repository = repository_factory()
        mediator = CqrsMediator(None)
        mediator.register_handler(CreateConversationCommand, CreateConversationHandler(CreateConversationUseCase(repository, outbox)))
        mediator.register_handler(AppendMessageCommand, AppendMessageHandler(AppendMessageUseCase(repository, outbox)))
        mediator.register_handler(DeleteConversationCommand, DeleteConversationHandler(DeleteConversationUseCase(repository, outbox)))
        mediator.register_handler(GetConversationQuery, GetConversationHandler(GetConversationUseCase(repository)))
        mediator.register_handler(ListConversationsQuery, ListConversationsHandler(ListConversationsUseCase(repository)))
        _runtime = ChatRuntime(repository_factory=repository_factory, uow_factory=None, mediator=mediator, outbox=outbox, outbox_worker=None)
        return _runtime

    bootstrap_database = create_database_bootstrap(settings.persistence_provider)
    business_engine = create_chat_engine(settings.business_database_url)
    await bootstrap_database(
        settings.business_database_url,
        "projects/optimalleads/chat/infrastructure/persistence/alembic",
        settings.reset_database_on_startup,
    )
    business_session_factory = create_chat_session_factory(business_engine)
    outbox = build_chat_outbox_factory(business_session_factory())
    app_settings = get_settings()
    broker = build_broker(app_settings)
    dispatcher = build_dispatcher(broker)
    outbox_worker = ChatOutboxWorker(outbox, dispatcher)

    repository_factory = build_chat_repository_factory(business_session_factory)
    uow_factory = build_chat_uow_factory(business_session_factory)
    mediator = CqrsMediator(uow_factory)
    logger.info(
        "chat.runtime.sql.ready",
        extra={
            "uow_type": type(uow_factory()).__name__,
            "session_factory_type": type(business_session_factory).__name__,
        },
    )
    command_repository = repository_factory()
    logger.info("chat.runtime.sql.command_repository.ready", extra={"repository_type": type(command_repository).__name__})
    mediator.register_handler(CreateConversationCommand, CreateConversationHandler(CreateConversationUseCase(command_repository, outbox)))
    mediator.register_handler(AppendMessageCommand, AppendMessageHandler(AppendMessageUseCase(command_repository, outbox)))
    mediator.register_handler(DeleteConversationCommand, DeleteConversationHandler(DeleteConversationUseCase(command_repository, outbox)))
    mediator.register_handler(GetConversationQuery, GetConversationHandler(GetConversationUseCase(command_repository)))
    mediator.register_handler(ListConversationsQuery, ListConversationsHandler(ListConversationsUseCase(command_repository)))
    _runtime = ChatRuntime(repository_factory=repository_factory, uow_factory=uow_factory, mediator=mediator, outbox=outbox, outbox_worker=outbox_worker)
    return _runtime


def reset_chat_runtime() -> None:
    global _runtime
    _runtime = None
