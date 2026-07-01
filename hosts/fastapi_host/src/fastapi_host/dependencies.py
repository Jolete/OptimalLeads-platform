from __future__ import annotations

from projects.chat.application.use_cases.ask_use_case import AskUseCase
from fastapi_host.program import get_container


def get_ask_use_case() -> AskUseCase:
    return get_container().ask_use_case()
