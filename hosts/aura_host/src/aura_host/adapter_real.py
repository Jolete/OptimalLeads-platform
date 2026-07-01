from __future__ import annotations

from llm_application.chat.dtos import AskCommand, AskResult
from llm_infrastructure.composition.container import Container


class AuraRequest:
    """Model que simula una request del teu Aura framework."""

    def __init__(self, session_id: str, prompt: str, context: dict[str, str] | None = None) -> None:
        self.session_id = session_id
        self.prompt = prompt
        self.context = context or {}


class AuraResponse:
    """Model que simula una response del teu Aura framework."""

    def __init__(
        self,
        reply: str,
        model: str,
        session_id: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.reply = reply
        self.model = model
        self.session_id = session_id
        self.metadata = metadata or {}


class AuraAdapterReal:
    """
    Adapter REAL que connecta el teu framework Aura amb el sistema.

    El teu Aura framework crida alguna cosa tipus:
        aura_adapter.process(AuraRequest(...))

    I el teu Aura rep la AuraResponse.

    Tot el que passa a dins és transparent per Aura:
    - LLM provider? CommandBus? Infrastructure? Aura no ho sap.
    - Aura només veu Request → Response.
    """

    def __init__(self, container: Container | None = None) -> None:
        self._container = container or Container()

    async def process(self, request: AuraRequest) -> AuraResponse:
        """
        Processa una request del teu Aura framework.
        """
        command = AskCommand(
            conversation_id=request.session_id,
            message=request.prompt,
        )
        result: AskResult = await self._container.ask_use_case().execute(command)

        return AuraResponse(
            reply=result.answer,
            model=result.model,
            session_id=request.session_id,
            metadata={"context": str(request.context)},
        )


# Exemple d'ús:
# adapter = AuraAdapterReal()
#
# request = AuraRequest(
#     session_id="aura-sess-123",
#     prompt="Escriu un poema curt",
#     context={"language": "ca", "tone": "epic"}
# )
#
# response = await adapter.process(request)
# print(f"Aura reply: {response.reply}")
# print(f"Model: {response.model}")
