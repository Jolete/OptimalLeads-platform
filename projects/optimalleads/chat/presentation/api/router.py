from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core_domain import ValidationError
from projects.optimalleads.chat.application.dto import AppendMessageCommand, CreateConversationCommand
from projects.optimalleads.chat.application.dto import DeleteConversationCommand, GetConversationQuery, ListConversationsQuery
from projects.optimalleads.chat.application.exceptions import ConversationNotFoundError
from projects.optimalleads.chat.application.use_cases import GetConversationUseCase, ListConversationsUseCase
from projects.optimalleads.chat.infrastructure.persistence.bootstrap import get_chat_runtime

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


class CreateConversationRequest(BaseModel):
    title: str
    correlation_id: str | None = None


class AppendMessageRequest(BaseModel):
    message: str
    correlation_id: str | None = None


async def _get_runtime():
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
    request = CreateConversationCommand(title=payload.title, correlation_id=payload.correlation_id)
    conversation = await _run_command(request)
    return _serialize_conversation(conversation)


@router.post("/conversations/{conversation_id}/messages")
async def append_message(conversation_id: str, payload: AppendMessageRequest) -> dict[str, object]:
    request = AppendMessageCommand(
        conversation_id=conversation_id,
        message=payload.message,
        correlation_id=payload.correlation_id,
    )
    try:
        conversation = await _run_command(request)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return _serialize_conversation(conversation)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict[str, object]:
    _ = GetConversationQuery(conversation_id=conversation_id)
    runtime = await _get_runtime()
    conversation = await GetConversationUseCase(runtime.repository).execute(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return _serialize_conversation(conversation)


@router.get("/conversations")
async def list_conversations() -> list[dict[str, object]]:
    _ = ListConversationsQuery()
    runtime = await _get_runtime()
    conversations = await ListConversationsUseCase(runtime.repository).execute()
    return [_serialize_conversation(conversation) for conversation in conversations]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, correlation_id: str | None = None) -> dict[str, str]:
    request = DeleteConversationCommand(conversation_id=conversation_id, correlation_id=correlation_id)
    try:
        await _run_command(request)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return {"status": "deleted", "conversation_id": conversation_id}


@router.get("/outbox")
async def get_outbox() -> list[dict[str, object]]:
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


async def ensure_chat_schema() -> None:
    await _get_runtime()
