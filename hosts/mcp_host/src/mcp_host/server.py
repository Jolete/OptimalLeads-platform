from __future__ import annotations

from projects.chat.application.dto.ask_command import AskCommand
from projects.chat.application.dto.ask_result import AskResult
from projects.chat.infrastructure.composition.container import Container


class MCPServerAdapter:
    """Exemple de host MCP.

    La teva llibreria/framework MCP real registraria eines i delegaria cap a aquest adapter.
    """

    def __init__(self, container: Container | None = None) -> None:
        self._container = container or Container()

    async def handle_chat_tool(self, conversation_id: str, message: str) -> AskResult:
        command = AskCommand(conversation_id=conversation_id, message=message)
        return await self._container.command_bus().send(command)
