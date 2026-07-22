from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from core_domain import EventEnvelope
from core_infrastructure.drivers.sqlserver.database_composition import bootstrap_sqlserver_database
from projects.optimalleads.saga.process_manager import SagaProgress, SagaStatus
from .models import SagaEventAttemptRow, SagaProcessedEventRow


class SqlAlchemySagaStateRepository:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def has_processed(self, event_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.execute(select(SagaProcessedEventRow.event_id).where(SagaProcessedEventRow.event_id == event_id))
            return result.scalar_one_or_none() is not None

    async def mark_processed(self, event: EventEnvelope) -> None:
        async with self._session_factory() as session:
            await session.merge(
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
                select(SagaProcessedEventRow)
                .where(SagaProcessedEventRow.correlation_id == correlation_id)
                .order_by(SagaProcessedEventRow.processed_at.desc())
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
                completed_steps=[],
                last_error=row.last_error,
            )

    async def save_progress(self, progress: SagaProgress) -> None:
        async with self._session_factory() as session:
            row = await session.get(SagaProcessedEventRow, progress.event_id)
            if row is None:
                row = SagaProcessedEventRow(
                    event_id=progress.event_id,
                    saga_id=progress.correlation_id,
                    event_name=progress.event_name,
                    aggregate_id=progress.aggregate_id,
                    correlation_id=progress.correlation_id,
                    processed_at=datetime.utcnow(),
                    completed_steps_json=json.dumps(progress.completed_steps),
                )
                session.add(row)

            row.saga_id = progress.correlation_id
            row.event_name = progress.event_name
            row.aggregate_id = progress.aggregate_id
            row.correlation_id = progress.correlation_id
            row.status = progress.status.value
            row.current_phase = progress.current_phase
            row.completed_steps_json = json.dumps(progress.completed_steps)
            row.last_error = progress.last_error
            await session.commit()

    async def record_attempt_start(self, event: EventEnvelope, attempt_number: int) -> str:
        attempt_id = str(uuid.uuid4())
        async with self._session_factory() as session:
            session.add(
                SagaEventAttemptRow(
                    attempt_id=attempt_id,
                    event_id=event.event_id,
                    saga_id=event.correlation_id,
                    event_name=event.event_name,
                    attempt_number=attempt_number,
                    status="started",
                    started_at=datetime.utcnow(),
                )
            )
            await session.commit()
        return attempt_id

    async def record_attempt_finish(self, attempt_id: str, status: str, error: str | None = None) -> None:
        async with self._session_factory() as session:
            row = await session.get(SagaEventAttemptRow, attempt_id)
            if row is None:
                return
            row.status = status
            row.error = error
            row.finished_at = datetime.utcnow()
            await session.commit()


async def build_saga_state_repository(database_url: str, reset_database_on_startup: bool = False) -> SqlAlchemySagaStateRepository:
    await bootstrap_sqlserver_database(
        database_url,
        "projects/optimalleads/saga/infrastructure/persistence/alembic",
        reset_database_on_startup,
    )
    engine = create_async_engine(database_url, future=True)
    return SqlAlchemySagaStateRepository(async_sessionmaker(engine, expire_on_commit=False))