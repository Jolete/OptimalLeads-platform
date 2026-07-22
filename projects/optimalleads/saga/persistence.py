from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core_domain import EventEnvelope
from core_infrastructure.drivers.sqlserver.database_bootstrap import drop_database_if_exists, ensure_database_exists
from .process_manager import SagaProgress, SagaStatus


class SagaBase(DeclarativeBase):
    pass


class SagaProcessedEventRow(SagaBase):
    __tablename__ = "optimalleads_saga_processed_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    saga_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=SagaStatus.RECEIVED.value)
    current_phase: Mapped[str] = mapped_column(String(255), nullable=False, default="received")
    completed_steps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class SqlAlchemySagaStateRepository:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def has_processed(self, event_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(select(SagaProcessedEventRow.event_id).where(SagaProcessedEventRow.event_id == event_id))
            return result.scalar_one_or_none() is not None

    async def mark_processed(self, event: EventEnvelope) -> None:
        async with self._session_factory() as session:
            session.add(
                SagaProcessedEventRow(
                    event_id=event.event_id,
                    saga_id=event.correlation_id,
                    event_name=event.event_name,
                    aggregate_id=event.aggregate_id,
                    correlation_id=event.correlation_id,
                )
            )
            await session.commit()

    async def load_progress(self, correlation_id: str) -> SagaProgress | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(SagaProcessedEventRow).where(SagaProcessedEventRow.correlation_id == correlation_id).order_by(SagaProcessedEventRow.processed_at.desc())
            )
            row = result.scalars().first()
            if row is None:
                return None
            return SagaProgress(
                event_id=row.event_id,
                event_name=row.event_name,
                correlation_id=row.correlation_id,
                causation_id=None,
                aggregate_id=row.aggregate_id,
                status=SagaStatus(row.status),
                current_phase=row.current_phase,
                completed_steps=json.loads(row.completed_steps_json or "[]"),
                last_error=row.last_error,
            )

    async def save_progress(self, progress: SagaProgress) -> None:
        async with self._session_factory() as session:
            row = SagaProcessedEventRow(
                event_id=progress.event_id,
                saga_id=progress.correlation_id,
                event_name=progress.event_name,
                aggregate_id=progress.aggregate_id,
                correlation_id=progress.correlation_id,
                status=progress.status.value,
                current_phase=progress.current_phase,
                completed_steps_json=json.dumps(progress.completed_steps),
                last_error=progress.last_error,
            )
            await session.merge(row)
            await session.commit()


async def build_saga_state_repository(database_url: str, reset_database_on_startup: bool = False) -> SqlAlchemySagaStateRepository:
    if reset_database_on_startup:
        await drop_database_if_exists(database_url)
    await ensure_database_exists(database_url)
    engine = create_async_engine(database_url, future=True)
    async with engine.begin() as connection:
        await connection.run_sync(SagaBase.metadata.create_all)
    return SqlAlchemySagaStateRepository(async_sessionmaker(engine, expire_on_commit=False))