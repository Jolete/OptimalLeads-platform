from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core_domain.messaging import CqrsMediator
from core_infrastructure.composition_root.persistence_composition import build_broker, build_dispatcher
from core_infrastructure.drivers.sqlserver import bootstrap_sqlserver_database  # noqa: F401
from core_infrastructure.persistence.persistence_factory import create_database_bootstrap
from core_infrastructure.services import OutboxWorker
from core_domain.pipeline.transaction_behavior import get_current_unit_of_work

from projects.optimalleads.chat.application.dto import AppendMessageCommand, CreateConversationCommand, DeleteConversationCommand
from projects.optimalleads.chat.application.handlers import AppendMessageHandler, CreateConversationHandler, DeleteConversationHandler
from projects.optimalleads.chat.application.use_cases import AppendMessageUseCase, CreateConversationUseCase, DeleteConversationUseCase
from projects.optimalleads.chat.infrastructure.persistence.database import create_chat_engine, create_chat_session_factory
from projects.optimalleads.chat.infrastructure.persistence.factory import build_chat_memory_runtime, build_chat_outbox_factory, build_chat_repository_factory, build_chat_uow_factory
from projects.optimalleads.chat.infrastructure.persistence.settings import get_persistence_settings
from projects.optimalleads.chat.infrastructure.persistence.models.outbox import ChatOutboxRow
from projects.optimalleads.chat.infrastructure.services.outbox_worker import ChatOutboxWorker
from projects.optimalleads.chat.settings import get_settings


@dataclass(slots=True)
class ChatRuntime:
    repository_factory: Callable[[], object]
    repository: object
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
        _runtime = ChatRuntime(repository_factory=repository_factory, repository=repository, uow_factory=None, mediator=mediator, outbox=outbox, outbox_worker=None)
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
    mediator.register_handler(CreateConversationCommand, CreateConversationHandler(CreateConversationUseCase(_uow_repository("conversation"), outbox)))
    mediator.register_handler(AppendMessageCommand, AppendMessageHandler(AppendMessageUseCase(_uow_repository("conversation"), outbox)))
    mediator.register_handler(DeleteConversationCommand, DeleteConversationHandler(DeleteConversationUseCase(_uow_repository("conversation"), outbox)))
    _runtime = ChatRuntime(repository_factory=repository_factory, repository=repository_factory(), uow_factory=uow_factory, mediator=mediator, outbox=outbox, outbox_worker=outbox_worker)
    return _runtime


def _uow_repository(name: str):
    class _RepositoryProxy:
        async def add(self, entity):
            return await get_current_unit_of_work().get_repository(name).add(entity)

        async def save(self, entity):
            return await get_current_unit_of_work().get_repository(name).save(entity)

        async def delete_by_id(self, entity_id):
            return await get_current_unit_of_work().get_repository(name).delete_by_id(entity_id)

        async def get(self, entity_id):
            return await get_current_unit_of_work().get_repository(name).get(entity_id)

        async def all(self):
            return await get_current_unit_of_work().get_repository(name).all()

    return _RepositoryProxy()
