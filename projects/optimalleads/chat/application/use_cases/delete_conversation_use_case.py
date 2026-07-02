from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationId

logger = logging.getLogger(__name__)


class DeleteConversationUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId], outbox: ChatOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, conversation_id: str, correlation_id: str | None = None) -> None:
        logger.info("chat.conversation.delete.start", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        conversation = await self._repository.get(conversation_id)
        if conversation is None:
            logger.warning("chat.conversation.delete.not_found", extra={"conversation_id": conversation_id})
            raise ConversationNotFoundError(conversation_id)

        await self._repository.delete_by_id(conversation_id)
        correlation_id = correlation_id or conversation_id
        logger.info("chat.conversation.deleted", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=conversation_id,
                event_name="ConversationDeleted",
                event_kind=EventKind.DOMAIN,
                correlation_id=correlation_id,
                causation_id=None,
                occurred_at=datetime.now(timezone.utc).isoformat(),
                payload={"conversation_id": conversation_id},
            )
        )
        logger.info("chat.conversation.delete.done", extra={"conversation_id": conversation_id})
