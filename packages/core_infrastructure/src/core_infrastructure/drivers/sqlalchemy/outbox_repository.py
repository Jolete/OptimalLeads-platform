from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core_domain import EventEnvelope, OutboxPort


RowType = TypeVar("RowType")


class SqlAlchemyOutboxRepository(OutboxPort, Generic[RowType]):
    """Reusable SQLAlchemy-backed outbox implementation.

    One row is persisted per EventEnvelope. `aggregate_id` identifies the
    aggregate that produced the event; `event_id` identifies the envelope row.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        session: AsyncSession | None = None,
        model_type: type[RowType] | None = None,
        row_factory: Callable[[EventEnvelope], RowType] | None = None,
        event_factory: Callable[[RowType], EventEnvelope] | None = None,
        auto_commit: bool = True,
    ) -> None:
        if session_factory is None and session is None:
            raise ValueError("A session or session_factory is required")

        self._session_factory = session_factory
        self._session = session
        self._model_type = model_type
        self._row_factory = row_factory
        self._event_factory = event_factory
        self._auto_commit = auto_commit

    async def add(self, event: EventEnvelope) -> None:
        row = self._row_factory(event) if self._row_factory is not None else event
        session = await self._resolve_session()
        session.add(row)
        if self._auto_commit:
            await session.flush()
            await session.commit()

    async def drain(self) -> list[EventEnvelope]:
        session = await self._resolve_session()
        if self._model_type is None or self._event_factory is None:
            raise ValueError("model_type and event_factory are required to drain outbox rows")

        try:
            result = await session.execute(select(self._model_type))
            rows = result.scalars().all()
            return [self._event_factory(row) for row in rows]
        except Exception:
            import logging

            logging.getLogger(__name__).exception("sqlalchemy.outbox.drain.failed", extra={"model_type": self._model_type.__name__ if self._model_type is not None else None})
            raise

    async def mark_published(self, events: list[EventEnvelope]) -> None:
        if not events:
            return
        session = await self._resolve_session()
        if self._model_type is None:
            raise ValueError("model_type is required to mark outbox rows as published")

        event_ids = [event.event_id for event in events]
        await session.execute(delete(self._model_type).where(self._model_type.event_id.in_(event_ids)))
        await session.commit()

    async def _resolve_session(self) -> AsyncSession:
        if self._session is not None:
            return self._session
        if self._session_factory is None:
            raise RuntimeError("Outbox repository is not configured with a session source")
        return self._session_factory()