from __future__ import annotations

from fastapi import APIRouter, Depends

from projects.chat.application.chat.dtos import AskCommand, AskResult
from projects.chat.application.chat.use_cases import AskUseCase
from projects.chat.infrastructure.composition.container import Container

router = APIRouter(tags=["chat"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=AskResult)
async def ask(
    command: AskCommand,
) -> AskResult:
    return await Container().ask_use_case().execute(command)
