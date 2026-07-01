from __future__ import annotations

import pytest

from projects.optimalleads.chat.domain import Conversation
from projects.optimalleads.chat.infrastructure.memory import InMemoryChatOutbox, InMemoryConversationRepository


@pytest.mark.asyncio
async def test_in_memory_conversation_repository_roundtrip() -> None:
    repository = InMemoryConversationRepository()
    conversation = Conversation(conversation_id="conv-1", title="Sales")

    await repository.save(conversation)

    loaded = await repository.get("conv-1")
    assert loaded is not None
    assert loaded.title == "Sales"


@pytest.mark.asyncio
async def test_in_memory_outbox_drains_events() -> None:
    outbox = InMemoryChatOutbox()

    assert await outbox.drain() == []
