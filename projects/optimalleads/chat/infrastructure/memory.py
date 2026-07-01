from __future__ import annotations

from core_domain import EventEnvelope, Specification
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain import Conversation, ConversationId


class InMemoryConversationRepository:
    def __init__(self) -> None:
        self.items: dict[str, Conversation] = {}

    async def add(self, entity: Conversation) -> ConversationId:
        self.items[str(entity.id.value)] = entity
        return entity.id

    async def get(self, id_: str | ConversationId) -> Conversation | None:
        key = str(id_.value) if isinstance(id_, ConversationId) else str(id_)
        return self.items.get(key)

    async def update(self, entity: Conversation) -> None:
        self.items[str(entity.id.value)] = entity

    async def remove(self, entity: Conversation) -> None:
        id_str = str(entity.id.value)
        if id_str in self.items:
            del self.items[id_str]

    async def exists(self, id_: ConversationId) -> bool:
        return str(id_.value) in self.items

    async def list(self) -> list[Conversation]:
        return list(self.items.values())

    async def save(self, entity: Conversation) -> Conversation:
        self.items[str(entity.id.value)] = entity
        return entity

    async def delete_by_id(self, id_: ConversationId) -> None:
        id_str = str(id_.value)
        if id_str in self.items:
            del self.items[id_str]

    async def search(self, criteria: Specification[Conversation]) -> list[Conversation]:
        return [item for item in self.items.values() if criteria.is_satisfied_by(item)]


class InMemoryChatOutbox(ChatOutboxPort):
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    async def add(self, event: EventEnvelope) -> None:
        self.events.append(event)

    async def drain(self) -> list[EventEnvelope]:
        events = list(self.events)
        self.events.clear()
        return events
