from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from core_domain.pipeline.transaction_behavior import get_current_unit_of_work
from projects.optimalleads.chat.application.dto import CreateConversationCommand
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationCreated, ConversationId, ConversationTitle

logger = logging.getLogger(__name__)


class CreateConversationUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId], outbox: ChatOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    def _resolve_repository(self) -> Repository[Conversation, ConversationId]:
        try:
            uow = get_current_unit_of_work()
        except RuntimeError:
            return self._repository
        try:
            return uow.get_repository("conversation")  # type: ignore[return-value]
        except Exception:
            logger.exception("chat.conversation.resolve_repository.failed")
            raise

    def _resolve_outbox(self) -> ChatOutboxPort:
        try:
            uow = get_current_unit_of_work()
        except RuntimeError:
            return self._outbox
        try:
            return uow.get_repository("outbox")  # type: ignore[return-value]
        except Exception:
            logger.exception("chat.conversation.resolve_outbox.failed")
            raise

    async def execute(self, input_data: CreateConversationCommand) -> Conversation:
        logger.info("chat.conversation.create.start", extra={"title": input_data.title, "correlation_id": input_data.correlation_id})
        conversation = Conversation(id=ConversationId.create_unique(), title=ConversationTitle.create(input_data.title))
        try:
            repository = self._resolve_repository()
            outbox = self._resolve_outbox()
            await repository.add(conversation)
            conversation_id = str(conversation.id.value)
            event = ConversationCreated(conversation_id=conversation.id, title=conversation.title)
            correlation_id = input_data.correlation_id or conversation_id
            logger.info("chat.conversation.created", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
            await outbox.add(
                EventEnvelope(
                    event_id=str(uuid4()),
                    aggregate_id=conversation_id,
                    event_name="ConversationCreated",
                    event_kind=EventKind.DOMAIN,
                    correlation_id=correlation_id,
                    causation_id=None,
                    occurred_at=datetime.now(timezone.utc).isoformat(),
                    payload={"conversation_id": str(event.conversation_id.value), "title": event.title.value},
                )
            )
            logger.info("chat.conversation.create.done", extra={"conversation_id": conversation_id})
            return conversation
        except Exception:
            logger.exception("chat.conversation.create.failed", extra={"title": input_data.title, "correlation_id": input_data.correlation_id})
            raise
