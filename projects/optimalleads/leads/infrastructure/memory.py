from __future__ import annotations

from core_domain import EventEnvelope, Specification
from projects.optimalleads.leads.application.ports import LeadsOutboxPort
from projects.optimalleads.leads.domain import Lead, LeadId


class InMemoryLeadRepository:
    def __init__(self) -> None:
        self.items: dict[str, Lead] = {}

    async def add(self, entity: Lead) -> LeadId:
        self.items[str(entity.id.value)] = entity
        return entity.id

    async def get(self, id_: str | LeadId) -> Lead | None:
        key = str(id_.value) if isinstance(id_, LeadId) else str(id_)
        return self.items.get(key)

    async def update(self, entity: Lead) -> None:
        self.items[str(entity.id.value)] = entity

    async def remove(self, entity: Lead) -> None:
        id_str = str(entity.id.value)
        if id_str in self.items:
            del self.items[id_str]

    async def exists(self, id_: LeadId) -> bool:
        return str(id_.value) in self.items

    async def list(self) -> list[Lead]:
        return list(self.items.values())

    async def save(self, entity: Lead) -> Lead:
        self.items[str(entity.id.value)] = entity
        return entity

    async def delete_by_id(self, id_: LeadId) -> None:
        id_str = str(id_.value)
        if id_str in self.items:
            del self.items[id_str]

    async def search(self, criteria: Specification[Lead]) -> list[Lead]:
        return [item for item in self.items.values() if criteria.is_satisfied_by(item)]


class InMemoryLeadOutbox(LeadsOutboxPort):
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []

    async def add(self, event: EventEnvelope) -> None:
        self.events.append(event)

    async def drain(self) -> list[EventEnvelope]:
        events = list(self.events)
        self.events.clear()
        return events
