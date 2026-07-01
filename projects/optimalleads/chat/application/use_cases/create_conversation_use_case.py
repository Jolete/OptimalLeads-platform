from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from core_domain import EventEnvelope, EventKind, Repository
from projects.optimalleads.chat.application.dto import CreateConversationCommand
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationCreated, ConversationId, ConversationTitle

logger = logging.getLogger(__name__)


class CreateConversationUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId], outbox: ChatOutboxPort) -> None:
        self._repository = repository
        self._outbox = outbox

    async def execute(self, input_data: CreateConversationCommand) -> Conversation:
        conversation = Conversation(id=ConversationId.create_unique(), title=ConversationTitle.create(input_data.title))
        await self._repository.add(conversation)
        conversation_id = str(conversation.id.value)
        event = ConversationCreated(conversation_id=conversation.id, title=conversation.title)
        correlation_id = input_data.correlation_id or conversation_id
        logger.info("chat.conversation.created", extra={"conversation_id": conversation_id, "correlation_id": correlation_id})
        await self._outbox.add(
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
        return conversation
