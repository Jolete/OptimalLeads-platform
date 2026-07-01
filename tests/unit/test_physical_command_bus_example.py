from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "core_domain" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "core_application" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "core_infrastructure" / "src"))
sys.path.insert(0, str(ROOT / "projects"))

from projects.chat.application.dto.ask_command import AskCommand
from projects.chat.infrastructure.composition.container import Container
from core_infrastructure import Settings


@pytest.mark.asyncio
async def test_command_bus_routes_to_ask_use_case() -> None:
    container = Container(settings=Settings(llm_provider="echo"))

    result = await container.command_bus().send(
        AskCommand(conversation_id="bus-demo", message="hola")
    )

    assert result.answer == "[echo local] hola"
    assert result.model == "local-echo"
