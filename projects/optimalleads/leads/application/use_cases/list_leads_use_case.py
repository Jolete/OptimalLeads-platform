from __future__ import annotations

from core_domain import Repository
from projects.optimalleads.leads.domain import Lead, LeadId


class ListLeadsUseCase:
    def __init__(self, repository: Repository[Lead, LeadId]) -> None:
        self._repository = repository

    async def execute(self) -> list[Lead]:
        return await self._repository.all()
