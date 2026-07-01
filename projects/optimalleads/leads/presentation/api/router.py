from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core_domain import ValidationError
from projects.optimalleads.leads.application.dto import AdvanceLeadStageCommand, CreateLeadCommand, DeleteLeadCommand, GetLeadQuery, ListLeadsQuery, UpdateLeadCommand
from projects.optimalleads.leads.application.use_cases import (
    GetLeadUseCase,
    ListLeadsUseCase,
)
from projects.optimalleads.leads.infrastructure.persistence.bootstrap import get_leads_runtime

router = APIRouter(tags=["leads"])
logger = logging.getLogger(__name__)

_runtime = None


class CreateLeadRequest(BaseModel):
    name: str
    correlation_id: str | None = None


class UpdateLeadRequest(BaseModel):
    name: str
    stage: str | None = None
    correlation_id: str | None = None


class AdvanceLeadStageRequest(BaseModel):
    stage: str
    correlation_id: str | None = None


async def _get_runtime():
    global _runtime
    if _runtime is None:
        _runtime = await get_leads_runtime()
    return _runtime


async def _noop() -> None:
    return None


async def _run_command(request):
    runtime = await _get_runtime()
    if runtime.mediator is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="CQRS mediator is not available")

    try:
        return await runtime.mediator.send(request)
    except ValidationError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


def _serialize_lead(lead) -> dict[str, object]:
    return {
        "id": str(lead.id.value),
        "name": lead.name.value,
        "stage": lead.stage.value,
        "notes": list(lead.notes),
    }


@router.get("/health")
async def health() -> dict[str, str]:
    logger.info("leads.health")
    return {"service": "leads", "status": "ok"}


@router.post("/leads")
async def create_lead(payload: CreateLeadRequest) -> dict[str, object]:
    logger.info("leads.create.request", extra={"name": payload.name, "has_correlation_id": payload.correlation_id is not None})
    request = CreateLeadCommand(name=payload.name, correlation_id=payload.correlation_id)
    try:
        lead = await _run_command(request)
    except Exception:
        logger.exception("leads.create.failed", extra={"has_correlation_id": payload.correlation_id is not None})
        raise
    logger.info("leads.create.success", extra={"lead_id": str(lead.id.value)})
    return _serialize_lead(lead)


@router.post("/leads/{lead_id}/stage")
async def advance_stage(lead_id: str, payload: AdvanceLeadStageRequest) -> dict[str, object]:
    request = AdvanceLeadStageCommand(lead_id=lead_id, stage=payload.stage, correlation_id=payload.correlation_id)
    lead = await _run_command(request)
    return _serialize_lead(lead)


@router.get("/leads/{lead_id}")
async def get_lead(lead_id: str) -> dict[str, object]:
    _ = GetLeadQuery(lead_id=lead_id)
    runtime = await _get_runtime()
    lead = await GetLeadUseCase(runtime.repository).execute(lead_id)
    if lead is None:
        return {"lead_id": lead_id, "name": "", "stage": "", "notes": []}
    return {
        "id": str(lead.id.value),
        "name": lead.name.value,
        "stage": lead.stage.value,
        "notes": list(lead.notes),
    }


@router.get("/leads")
async def list_leads() -> list[dict[str, object]]:
    _ = ListLeadsQuery()
    runtime = await _get_runtime()
    logger.info("leads.list.request")
    try:
        leads = await ListLeadsUseCase(runtime.repository).execute()
    except Exception:
        logger.exception("leads.list.failed")
        raise
    logger.info("leads.list.success", extra={"count": len(leads)})
    return [
        {
            "id": str(lead.id.value),
            "name": lead.name.value,
            "stage": lead.stage.value,
            "notes": list(lead.notes),
        }
        for lead in leads
    ]


@router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, payload: UpdateLeadRequest) -> dict[str, object]:
    request = UpdateLeadCommand(lead_id=lead_id, name=payload.name, stage=payload.stage, correlation_id=payload.correlation_id)
    lead = await _run_command(request)
    return _serialize_lead(lead)


@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, correlation_id: str | None = None) -> dict[str, str]:
    request = DeleteLeadCommand(lead_id=lead_id, correlation_id=correlation_id)
    try:
        await _run_command(request)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return {"status": "deleted", "lead_id": request.lead_id}


@router.get("/outbox")
async def outbox_view() -> list[dict[str, object]]:
    runtime = await _get_runtime()
    return [event.model_dump() for event in await runtime.outbox.drain()]


@router.post("/outbox/flush")
async def flush_outbox() -> dict[str, int]:
    runtime = await _get_runtime()
    if runtime.outbox_worker is None:
        published = len(await runtime.outbox.drain())
    else:
        published = await runtime.outbox_worker.flush()
    return {"published": published}
