from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from core_domain import ValidationBehavior, ValidationError
from projects.optimalleads.analytics.application.dto import IngestEventCommand, ReadSnapshotQuery
from projects.optimalleads.analytics.infrastructure.persistence.bootstrap import get_analytics_runtime
from projects.optimalleads.analytics.presentation.contracts import IngestEventRequest

router = APIRouter(tags=["analytics"])
logger = logging.getLogger(__name__)

_runtime = None


async def _get_runtime():
    global _runtime
    if _runtime is None:
        _runtime = await get_analytics_runtime()
    return _runtime


async def _noop() -> None:
    return None


async def _validate_command(request) -> None:
    try:
        await ValidationBehavior().handle(request, _noop)
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


async def _run_command(request, handler):
    await _validate_command(request)
    return await handler()


async def _send(request):
    runtime = await _get_runtime()
    if runtime.mediator is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="CQRS mediator is not available")

    try:
        return await runtime.mediator.send(request)
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.get("/health")
async def health() -> dict[str, str]:
    logger.info("analytics.health")
    return {"service": "analytics", "status": "ok"}


async def _ingest(event: IngestEventRequest) -> dict[str, str]:
    logger.info("analytics.ingest.request", extra={"event_name": event.event_name, "aggregate_id": event.aggregate_id, "correlation_id": event.correlation_id})
    request = IngestEventCommand(event=IngestEventRequest.model_validate(event.model_dump()))
    await _run_command(request, lambda: _send(request))
    return {"status": "ingested"}


@router.post("/internal/events")
async def ingest_internal(event: IngestEventRequest) -> dict[str, str]:
    return await _ingest(event)


@router.post("/ingest")
async def ingest(event: IngestEventRequest) -> dict[str, str]:
    return await _ingest(event)


async def _read_snapshot() -> dict[str, object]:
    request = ReadSnapshotQuery()
    snapshot = await _send(request)
    return {
        "id": snapshot.id.value,
        "conversations": {
            conversation_id: {
                "id": read_model.id,
                "title": read_model.title,
                "message_count": read_model.message_count,
            }
            for conversation_id, read_model in snapshot.conversations.items()
        },
        "leads": {
            lead_id: {
                "id": read_model.id,
                "name": read_model.name,
                "stage": read_model.stage,
            }
            for lead_id, read_model in snapshot.leads.items()
        },
    }


@router.get("/snapshot")
async def snapshot() -> dict[str, object]:
    return await _read_snapshot()


@router.get("/")
async def get_all() -> dict[str, object]:
    return await _read_snapshot()


@router.get("/outbox")
async def get_outbox() -> list[dict[str, object]]:
    return []


@router.post("/outbox/flush")
async def flush_outbox() -> dict[str, int]:
    return {"published": 0}

