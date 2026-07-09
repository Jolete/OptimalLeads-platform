from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi import Query
from pydantic import BaseModel

from core_domain import ValidationError
from projects.optimalleads.chat.application.dto import AppendMessageCommand, CreateConversationCommand
from projects.optimalleads.chat.application.dto import DeleteConversationCommand, GetConversationQuery, ListConversationsQuery
from projects.optimalleads.chat.application.dto import UpdateConversationCommand
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.infrastructure.persistence.bootstrap import get_chat_runtime, reset_chat_runtime

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


class CreateConversationRequest(BaseModel):
    title: str
    correlation_id: str | None = None


class AppendMessageRequest(BaseModel):
    message: str
    correlation_id: str | None = None


class UpdateConversationRequest(BaseModel):
    title: str
    summary: str | None = None
    messages: list[str] | None = None
    correlation_id: str | None = None


async def _get_runtime():
    # reset_chat_runtime()
    return await get_chat_runtime()


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


def _serialize_conversation(conversation) -> dict[str, object]:
    return {
        "conversation_id": str(conversation.id.value),
        "title": conversation.title.value,
        "messages": list(conversation.messages),
    }


@router.get("/health")
async def health() -> dict[str, str]:
    logger.info("chat.health")
    return {"service": "chat", "status": "ok"}


@router.post("/conversations")
async def create_conversation(payload: CreateConversationRequest) -> dict[str, object]:
    logger.info("chat.create.endpoint.request", extra={"title": payload.title, "has_correlation_id": payload.correlation_id is not None})
    request = CreateConversationCommand(title=payload.title, correlation_id=payload.correlation_id)
    try:
        conversation = await _run_command(request)
    except Exception:
        logger.exception("chat.create.endpoint.failed", extra={"title": payload.title, "has_correlation_id": payload.correlation_id is not None})
        raise
    logger.info("chat.create.endpoint.response", extra={"conversation_id": str(conversation.id.value)})
    return _serialize_conversation(conversation)


@router.post("/conversations/{conversation_id}/messages")
async def append_message(conversation_id: str, payload: AppendMessageRequest) -> dict[str, object]:
    logger.info("chat.append.endpoint.request", extra={"conversation_id": conversation_id, "has_correlation_id": payload.correlation_id is not None})
    request = AppendMessageCommand(
        conversation_id=conversation_id,
        message=payload.message,
        correlation_id=payload.correlation_id,
    )
    try:
        conversation = await _run_command(request)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    logger.info("chat.append.endpoint.response", extra={"conversation_id": conversation_id})
    return _serialize_conversation(conversation)


@router.put("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, payload: UpdateConversationRequest) -> dict[str, object]:
    logger.info("chat.update.endpoint.request", extra={"conversation_id": conversation_id, "has_correlation_id": payload.correlation_id is not None})
    request = UpdateConversationCommand(conversation_id=conversation_id, title=payload.title, summary=payload.summary, messages=payload.messages, correlation_id=payload.correlation_id)
    try:
        conversation = await _run_command(request)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    logger.info("chat.update.endpoint.response", extra={"conversation_id": conversation_id})
    return _serialize_conversation(conversation)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict[str, object]:
    runtime = await _get_runtime()
    conversation = await runtime.mediator.send(GetConversationQuery(conversation_id=conversation_id))
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return _serialize_conversation(conversation)


@router.get("/conversations")
async def list_conversations() -> list[dict[str, object]]:
    try:
        logger.info("chat.list.endpoint.start")
        runtime = await _get_runtime()
        # logger.info("chat.list.endpoint.runtime.ready", extra={"repository_type": type(runtime.repository).__name__})
        conversations = await runtime.mediator.send(ListConversationsQuery())
        logger.info("chat.list.endpoint.response", extra={"count": len(conversations)})
        return [_serialize_conversation(conversation) for conversation in conversations]
    except Exception:
        logger.exception("chat.list.endpoint.failed")
        raise


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, correlation_id: str | None = Query(default=None)) -> dict[str, str]:
    logger.info("chat.delete.endpoint.request", extra={"conversation_id": conversation_id, "has_correlation_id": correlation_id is not None})
    request = DeleteConversationCommand(conversation_id=conversation_id, correlation_id=correlation_id)
    try:
        await _run_command(request)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    logger.info("chat.delete.endpoint.response", extra={"conversation_id": conversation_id})
    return {"status": "deleted", "conversation_id": conversation_id}


@router.get("/outbox")
async def get_outbox() -> list[dict[str, object]]:
    runtime = await _get_runtime()
    return [event.model_dump() for event in await runtime.outbox.drain()]


@router.post("/outbox/flush")
async def flush_outbox() -> dict[str, int]:
    runtime = await _get_runtime()
    if runtime.outbox_worker is None:
        events = await runtime.outbox.drain()
        await runtime.outbox.mark_published(events)
        published = len(events)
    else:
        published = await runtime.outbox_worker.flush()
    return {"published": published}


async def ensure_chat_schema() -> None:
    await _get_runtime()
