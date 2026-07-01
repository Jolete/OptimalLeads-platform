from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConversationReadModel:
    id: str
    title: str
    message_count: int = 0
