from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "core_domain" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "core_application" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "core_infrastructure" / "src"))
sys.path.insert(0, str(ROOT / "projects"))
sys.path.insert(0, str(ROOT / "hosts" / "mcp_host" / "src"))
sys.path.insert(0, str(ROOT / "hosts" / "aura_host" / "src"))

from projects.chat.infrastructure.composition.container import Container
from core_infrastructure import Settings
from mcp_host.server_real import MCPServerRealSimulation
from aura_host.adapter_real import AuraAdapterReal, AuraRequest


@pytest.mark.asyncio
async def test_mcp_host_and_aura_host_both_use_same_underlying_logic() -> None:
    """
    Demostra que MCP host i Aura host són només adapters d'entrada.
    Tots dos deleguen al mateixa use case, mateix container.

    MCP client cridaria:
        server.execute_tool("ask_llm", {...})

    Aura client cridaria:
        adapter.process(AuraRequest(...))

    Resultat: la mateixa resposta, la mateixa lògica interna.
    """
    settings = Settings(llm_provider="echo")
    container = Container(settings=settings)

    # HOST 1: MCP Server
    mcp_server = MCPServerRealSimulation(container=container)
    mcp_result = await mcp_server.execute_tool(
        "ask_llm",
        {"conversation_id": "demo", "message": "Hola des de MCP"},
    )

    # HOST 2: Aura Adapter
    aura_adapter = AuraAdapterReal(container=container)
    aura_request = AuraRequest(
        session_id="demo",
        prompt="Hola des de Aura",
        context={"source": "aura"},
    )
    aura_response = await aura_adapter.process(aura_request)

    # Assertions
    assert mcp_result["answer"] == "[echo local] Hola des de MCP"
    assert mcp_result["model"] == "local-echo"

    assert aura_response.reply == "[echo local] Hola des de Aura"
    assert aura_response.model == "local-echo"

    # Tots dos han modificat la mateixa memòria!
    history = await container.memory().load("demo")
    # Hi ha 2 user + 2 assistant (un de cada host)
    assert len(history) == 4
    assert history[0].role == "user"
    assert history[0].content == "Hola des de MCP"
    assert history[2].role == "user"
    assert history[2].content == "Hola des de Aura"
