from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from core_domain.pipeline.transaction_behavior import get_current_unit_of_work
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationId, ConversationTitle

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

    async def execute(self, conversation_id: str, title: str, correlation_id: str | None = None) -> Conversation:
        logger.info("chat.conversation.update.start", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        repository = self._resolve_repository()
        outbox = self._resolve_outbox()
        conversation = await repository.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        conversation.update_title(title)
        await repository.save(conversation)
        correlation_id = correlation_id or conversation_id
        logger.info("chat.conversation.updated", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        await outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=conversation_id,
                event_name="ConversationUpdated",
                event_kind=EventKind.DOMAIN,
                correlation_id=correlation_id,
                causation_id=None,
                occurred_at=datetime.now(timezone.utc).isoformat(),
                payload={"conversation_id": conversation_id, "title": conversation.title.value},
            )
        )
        return conversation