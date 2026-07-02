from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from core_domain.pipeline.transaction_behavior import get_current_unit_of_work
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationId, ConversationMessage, ConversationTitle

logger = logging.getLogger(__name__)


class UpdateConversationUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId], outbox: ChatOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    def _resolve_repository(self) -> Repository[Conversation, ConversationId]:
        try:
            uow = get_current_unit_of_work()
        except RuntimeError:
            return self._repository
        return uow.get_repository("conversation")  # type: ignore[return-value]

    def _resolve_outbox(self) -> ChatOutboxPort:
        try:
            uow = get_current_unit_of_work()
        except RuntimeError:
            return self._outbox
        return uow.get_repository("outbox")  # type: ignore[return-value]

    async def execute(self, conversation_id: str, title: str, summary: str | None = None, messages: list[str] | None = None, correlation_id: str | None = None) -> Conversation:
        logger.info("chat.conversation.update.start", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        repository = self._resolve_repository()
        outbox = self._resolve_outbox()
        logger.info("chat.conversation.update.repository.resolved", extra={"conversation_id": conversation_id, "has_messages": messages is not None})
        conversation = await repository.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        logger.info("chat.conversation.update.entity.loaded", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        conversation.update_title(title)
        conversation.update_summary(summary)
        if messages is not None:
            validated_messages = [ConversationMessage.create(message).value for message in messages]
            conversation.update_messages(validated_messages)
            logger.info("chat.conversation.update.messages.assigned", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        logger.info("chat.conversation.update.before_save", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        await repository.save(conversation)
        logger.info("chat.conversation.update.after_save", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        correlation_id = correlation_id or conversation_id
        logger.info("chat.conversation.updated", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        logger.info("chat.conversation.update.before_outbox", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        await outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=conversation_id,
                event_name="ConversationUpdated",
                event_kind=EventKind.DOMAIN,
                correlation_id=correlation_id,
                causation_id=None,
                occurred_at=datetime.now(timezone.utc).isoformat(),
                payload={"conversation_id": conversation_id, "title": conversation.title.value, "summary": conversation.summary, "messages": list(conversation.messages)},
            )
        )
        logger.info("chat.conversation.update.after_outbox", extra={"conversation_id": conversation_id, "message_count": len(conversation.messages)})
        return conversation