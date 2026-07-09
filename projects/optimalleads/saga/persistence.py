from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core_domain import EventEnvelope
from core_infrastructure.drivers.sqlserver.database_bootstrap import ensure_database_exists


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


async def build_saga_state_repository(database_url: str) -> SqlAlchemySagaStateRepository:
    await ensure_database_exists(database_url)
    engine = create_async_engine(database_url, future=True)
    async with engine.begin() as connection:
        await connection.run_sync(SagaBase.metadata.create_all)
    return SqlAlchemySagaStateRepository(async_sessionmaker(engine, expire_on_commit=False))