from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from projects.optimalleads.chat.application.dto import AppendMessageCommand
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationMessage, ConversationMessageAppended, ConversationId

logger = logging.getLogger(__name__)


class AppendMessageUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId], outbox: ChatOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, input_data: AppendMessageCommand) -> Conversation:
        conversation = await self._repository.get(input_data.conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(input_data.conversation_id)

        conversation.append_message(input_data.message)
        await self._repository.save(conversation)
        event = ConversationMessageAppended(conversation_id=conversation.id, message=ConversationMessage.create(input_data.message))
        correlation_id = input_data.correlation_id or input_data.conversation_id
        logger.info("chat.message.appended", extra={"conversation_id": input_data.conversation_id, "correlation_id": correlation_id})
        await self._outbox.add(
            EventEnvelope(
                event_id=str(uuid4()),
                aggregate_id=input_data.conversation_id,
                event_name="ConversationMessageAppended",
                event_kind=EventKind.DOMAIN,
                correlation_id=correlation_id,
                causation_id=None,
                occurred_at=datetime.now(timezone.utc).isoformat(),
                payload={"conversation_id": str(event.conversation_id.value), "message": event.message.value},
            )
        )
        return conversation
