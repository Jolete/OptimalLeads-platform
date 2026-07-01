from __future__ import annotations

from core_domain import EventEnvelope, Specification
from projects.optimalleads.chat.application.ports import ChatOutboxPort
from projects.optimalleads.chat.domain import Conversation, ConversationId


class MemoryConversationRepository:
    def __init__(self) -> None:
        self._items: dict[str, Conversation] = {}

    async def add(self, entity: Conversation) -> ConversationId:
        self._items[str(entity.id.value)] = entity
        return entity.id

    async def get(self, id_: str | ConversationId) -> Conversation | None:
        key = str(id_.value) if isinstance(id_, ConversationId) else str(id_)
        return self._items.get(key)

    async def update(self, entity: Conversation) -> None:
        self._items[str(entity.id.value)] = entity

    async def remove(self, entity: Conversation) -> None:
        self._items.pop(str(entity.id.value), None)

    async def exists(self, id_: ConversationId) -> bool:
        return str(id_.value) in self._items

    async def list(self) -> list[Conversation]:
        return list(self._items.values())

    async def all(self) -> list[Conversation]:
        return await self.list()

    async def save(self, entity: Conversation) -> Conversation:
        self._items[str(entity.id.value)] = entity
        return entity

    async def delete_by_id(self, id_: ConversationId) -> None:
        self._items.pop(str(id_.value), None)

    async def search(self, criteria: Specification[Conversation]) -> list[Conversation]:
        return [item for item in self._items.values() if criteria.is_satisfied_by(item)]


class MemoryChatOutbox(ChatOutboxPort):
    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []

    async def add(self, event: EventEnvelope) -> None:
        self._events.append(event)

    async def drain(self) -> list[EventEnvelope]:
        events = list(self._events)
        self._events.clear()
        return events