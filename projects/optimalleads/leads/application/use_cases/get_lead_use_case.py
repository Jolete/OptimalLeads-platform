from __future__ import annotations

from core_domain import Repository
from projects.optimalleads.leads.domain import Lead, LeadId


class GetLeadUseCase:
    def __init__(self, repository: Repository[Lead, LeadId]) -> None:
        self._repository = repository

    async def execute(self, lead_id: str) -> Lead | None:
        return await self._repository.get(lead_id)
