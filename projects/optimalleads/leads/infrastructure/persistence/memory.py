from __future__ import annotations

from core_domain import EventEnvelope, Specification
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadId


class MemoryLeadRepository:
    def __init__(self) -> None:
        self._items: dict[str, Lead] = {}

    async def add(self, entity: Lead) -> LeadId:
        self._items[str(entity.id.value)] = entity
        return entity.id

    async def get(self, id_: str | LeadId) -> Lead | None:
        key = str(id_.value) if isinstance(id_, LeadId) else str(id_)
        return self._items.get(key)

    async def update(self, entity: Lead) -> None:
        self._items[str(entity.id.value)] = entity

    async def remove(self, entity: Lead) -> None:
        self._items.pop(str(entity.id.value), None)

    async def exists(self, id_: LeadId) -> bool:
        return str(id_.value) in self._items

    async def list(self) -> list[Lead]:
        return list(self._items.values())

    async def all(self) -> list[Lead]:
        return await self.list()

    async def all(self) -> list[Lead]:
        return await self.list()

    async def save(self, entity: Lead) -> Lead:
        self._items[str(entity.id.value)] = entity
        return entity

    async def delete_by_id(self, id_: LeadId) -> None:
        key = str(id_.value) if isinstance(id_, LeadId) else str(id_)
        self._items.pop(key, None)

    async def search(self, criteria: Specification[Lead]) -> list[Lead]:
        return [item for item in self._items.values() if criteria.is_satisfied_by(item)]


class MemoryLeadsOutbox(LeadsOutboxPort):
    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []

    async def add(self, event: EventEnvelope) -> None:
        self._events.append(event)

    async def drain(self) -> list[EventEnvelope]:
        events = list(self._events)
        self._events.clear()
        return events