from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from projects.optimalleads.analytics.application.ports import AnalyticsStorePort
from projects.optimalleads.analytics.domain import Snapshot
from projects.optimalleads.analytics.infrastructure.persistence.mappers import row_to_snapshot, snapshot_to_row
from projects.optimalleads.analytics.infrastructure.persistence.models.projection import ProjectionRow


class AnalyticsSnapshotStore(AnalyticsStorePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_snapshot(self, snapshot: Snapshot) -> None:
        await self._session.merge(snapshot_to_row(snapshot))

    async def get_snapshot(self) -> Snapshot:
        row = await self._session.get(ProjectionRow, "snapshot")
        if row is None:
            return Snapshot()
        return row_to_snapshot(row)
