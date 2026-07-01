from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from core_domain import EventEnvelope, EventKind
from core_infrastructure.drivers.sqlalchemy import OutboxRow, SqlAlchemyOutboxRepository, SqlAlchemyRepository
from core_infrastructure.persistence import SqlAlchemyUnitOfWork
from projects.optimalleads.chat.domain.conversation.entities.conversation import Conversation
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_id import ConversationId
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_title import ConversationTitle
from projects.optimalleads.chat.infrastructure.persistence.memory import MemoryChatOutbox, MemoryConversationRepository
from projects.optimalleads.chat.infrastructure.persistence.models.conversation import ConversationRow
from projects.optimalleads.chat.infrastructure.persistence.models.outbox import ChatOutboxRow


def build_chat_repository_factory(session_factory: Callable[[], object]) -> Callable[[], SqlAlchemyRepository[Conversation, str]]:
    return lambda: SqlAlchemyRepository[
        Conversation,
        str,
    ](
        session=session_factory(),
        model_type=ConversationRow,
        entity_factory=lambda row: Conversation(
            id=ConversationId.create(UUID(row.conversation_id)),
            title=ConversationTitle.create(row.title),
            messages=list(row.messages),
        ),
        model_factory=lambda conversation: ConversationRow(
            conversation_id=str(conversation.id.value),
            title=conversation.title.value,
            messages=list(conversation.messages),
        ),
        id_extractor=lambda row: row.conversation_id,
    )


def build_chat_outbox_factory(session: object) -> SqlAlchemyOutboxRepository[ChatOutboxRow]:
    return SqlAlchemyOutboxRepository[
        ChatOutboxRow,
    ](
        session=session,
        model_type=ChatOutboxRow,
        row_factory=lambda event: ChatOutboxRow(
            event_id=event.event_id,
            aggregate_id=event.aggregate_id,
            event_name=event.event_name,
            event_kind=event.event_kind.value,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            occurred_at=event.occurred_at,
            payload=event.payload,
        ),
        event_factory=lambda row: EventEnvelope(
            event_id=row.event_id,
            aggregate_id=row.aggregate_id,
            event_name=row.event_name,
            event_kind=EventKind(row.event_kind),
            correlation_id=row.correlation_id,
            causation_id=row.causation_id,
            occurred_at=row.occurred_at,
            payload=row.payload,
        ),
        auto_commit=False,
    )


def build_chat_uow_factory(session_factory: Callable[[], object]) -> Callable[[], SqlAlchemyUnitOfWork]:
    return lambda: SqlAlchemyUnitOfWork(
        session_factory=session_factory,
        repository_factories={
            "conversation": lambda session: SqlAlchemyRepository[
                Conversation,
                str,
            ](
                session=session,
                model_type=ConversationRow,
                entity_factory=lambda row: Conversation(
                    id=ConversationId.create(UUID(row.conversation_id)),
                    title=ConversationTitle.create(row.title),
                    messages=list(row.messages),
                ),
                model_factory=lambda conversation: ConversationRow(
                    conversation_id=str(conversation.id.value),
                    title=conversation.title.value,
                    messages=list(conversation.messages),
                ),
                id_extractor=lambda row: row.conversation_id,
                auto_commit=False,
            ),
            "outbox": lambda session: build_chat_outbox_factory(session),
        },
    )


def build_chat_memory_runtime() -> tuple[Callable[[], MemoryConversationRepository], MemoryChatOutbox]:
    return (lambda: MemoryConversationRepository(), MemoryChatOutbox())
