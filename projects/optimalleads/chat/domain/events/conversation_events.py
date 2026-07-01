from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationCreated:
    conversation_id: str
    title: str


@dataclass(frozen=True)
class ConversationMessageAppended:
    conversation_id: str
    message: str