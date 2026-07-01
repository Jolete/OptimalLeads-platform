from __future__ import annotations

from core_infrastructure.settings import Settings


class CompositionRoot:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.container = None