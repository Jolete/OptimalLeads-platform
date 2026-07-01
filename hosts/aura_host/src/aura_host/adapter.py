from __future__ import annotations

from projects.chat.application.dto.ask_command import AskCommand
from projects.chat.application.dto.ask_result import AskResult
from projects.chat.infrastructure.composition.container import Container


class AuraRequest:
    def __init__(self, session_id: str, prompt: str) -> None:
        self.session_id = session_id
        self.prompt = prompt


class AuraResponse:
    def __init__(self, reply: str, model: str) -> None:
        self.reply = reply
        self.model = model


class AuraAdapter:
    """Exemple d'adapter per al teu framework Aura."""

    def __init__(self, container: Container | None = None) -> None:
        self._container = container or Container()

    async def handle(self, request: AuraRequest) -> AuraResponse:
        result: AskResult = await self._container.ask_use_case().execute(
            AskCommand(conversation_id=request.session_id, message=request.prompt)
        )
        return AuraResponse(reply=result.answer, model=result.model)
