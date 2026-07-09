from __future__ import annotations

from pydantic import BaseModel, Field


class CreateLeadFromConversationRequest(BaseModel):
    conversation_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)