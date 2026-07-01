from __future__ import annotations


CHAT_CONVERSATIONS_TABLE_NAME = "chat_conversations"
CHAT_OUTBOX_TABLE_NAME = "chat_outbox"

CONVERSATION_TABLE_NAME = CHAT_CONVERSATIONS_TABLE_NAME
OUTBOX_TABLE_NAME = CHAT_OUTBOX_TABLE_NAME

# Keep table names explicit per service so each microservice owns its schema.