from __future__ import annotations

from typing import Any

from llm_application.chat.dtos import AskCommand, AskResult
from llm_infrastructure.composition.container import Container


class MCPTool:
    """Simulacio de tool MCP amb nom, descripció i paràmetres."""

    def __init__(self, name: str, description: str, schema: dict[str, Any]) -> None:
        self.name = name
        self.description = description
        self.schema = schema


class MCPServerRealSimulation:
    """
    Simulacio d'un servidor MCP REAL que:
    1. Registra tools MCP
    2. Rep crides de tool execution
    3. Delega al container/use case
    4. Retorna resultats
    """

    def __init__(self, container: Container | None = None) -> None:
        self._container = container or Container()
        self._tools: dict[str, MCPTool] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        """Registra els tools disponibles."""
        self._tools["ask_llm"] = MCPTool(
            name="ask_llm",
            description="Posa una pregunta a l'LLM dins d'una conversa",
            schema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["conversation_id", "message"],
            },
        )

    async def execute_tool(self, tool_name: str, arguments: dict[str, str]) -> dict[str, Any]:
        """
        Executa un tool MCP.
        Simulació del que faria el teu servidor MCP real.
        """
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' no registrat")

        if tool_name == "ask_llm":
            command = AskCommand(
                conversation_id=arguments["conversation_id"],
                message=arguments["message"],
            )
            result: AskResult = await self._container.command_bus().send(command)
            return {"answer": result.answer, "model": result.model}

        raise ValueError(f"Tool '{tool_name}' no implementat")

    def list_tools(self) -> list[MCPTool]:
        """Retorna els tools disponibles."""
        return list(self._tools.values())


# Exemple d'ús:
# server = MCPServerRealSimulation()
# tools = server.list_tools()
# for tool in tools:
#     print(f"- {tool.name}: {tool.description}")
#
# result = await server.execute_tool(
#     "ask_llm",
#     {"conversation_id": "demo", "message": "Hola"}
# )
# print(result)
