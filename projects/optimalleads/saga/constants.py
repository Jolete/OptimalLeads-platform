from __future__ import annotations

from pathlib import Path

SAGA_ENV_FILE = str(Path(__file__).resolve().parent / ".env")

SAGA_SERVICE_NAME = "optimalleads-saga"
SAGA_TITLE = "OptimalLeads Saga"
SAGA_OUTBOX_FLUSH_INTERVAL_SECONDS = 1.0
SAGA_INTERNAL_SERVICE_PROTOCOL_REST = "rest"
SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC = "grpc"
SAGA_DEFAULT_CHAT_CONSUMER_GROUP = "optimalleads-saga-chat-group"
SAGA_DEFAULT_LEADS_CONSUMER_GROUP = "optimalleads-saga-leads-group"
SAGA_DEFAULT_CHAT_RETRY_TOPIC = "optimalleads.chat.events.retry"
SAGA_DEFAULT_LEADS_RETRY_QUEUE = "optimalleads.leads.events.retry"
SAGA_DEFAULT_REPLAY_TOPIC = "optimalleads.saga.replay"
SAGA_INTERNAL_ANALYTICS_INGEST_EVENT_PATH = "/internal/events"
SAGA_INTERNAL_LEADS_CREATE_FROM_CONVERSATION_PATH = "/internal/leads/from-conversation"