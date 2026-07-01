from __future__ import annotations

import pytest

from projects.optimalleads.chat.application.dto import AppendMessageInput, CreateConversationInput
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.use_cases import AppendMessageUseCase, CreateConversationUseCase
from projects.optimalleads.chat.domain import Conversation, ConversationId


class InMemoryConversationRepository:
    def __init__(self) -> None:
        self.items: dict[str, Conversation] = {}

    async def get(self, id: str | ConversationId) -> Conversation | None:
        key = str(id.value) if isinstance(id, ConversationId) else str(id)
        return self.items.get(key)

    async def save(self, entity: Conversation) -> Conversation:
        self.items[str(entity.id.value)] = entity
        return entity


class InMemoryOutbox:
    def __init__(self) -> None:
        self.events = []

    async def add(self, event) -> None:
        self.events.append(event)

    async def drain(self):
        events = list(self.events)
        self.events.clear()
        return events


@pytest.mark.asyncio
async def test_create_conversation_emits_outbox_event() -> None:
    repository = InMemoryConversationRepository()
    outbox = InMemoryOutbox()
    use_case = CreateConversationUseCase(repository, outbox)

    conversation = await use_case.execute(CreateConversationInput(title="Demo", correlation_id="corr-1"))

    assert conversation.title.value == "Demo"
    assert len(outbox.events) == 1


@pytest.mark.asyncio
async def test_append_message_raises_when_missing_conversation() -> None:
    repository = InMemoryConversationRepository()
    outbox = InMemoryOutbox()
    use_case = AppendMessageUseCase(repository, outbox)

    with pytest.raises(ConversationNotFoundError):
        await use_case.execute(AppendMessageInput(conversation_id="missing", message="Hola"))
