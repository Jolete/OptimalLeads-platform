from __future__ import annotations

import logging
import importlib
from typing import Protocol

import httpx

from core_domain import EventEnvelope
from projects.optimalleads.analytics.presentation.contracts import IngestEventRequest as AnalyticsIngestEventRequest
from projects.optimalleads.leads.presentation.contracts import CreateLeadFromConversationRequest as LeadsCreateLeadFromConversationRequest
from projects.optimalleads.saga.constants import SAGA_INTERNAL_ANALYTICS_INGEST_EVENT_PATH, SAGA_INTERNAL_LEADS_CREATE_FROM_CONVERSATION_PATH, SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC, SAGA_INTERNAL_SERVICE_PROTOCOL_REST
from projects.optimalleads.saga.settings import SagaSettings

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional until grpc stubs are generated
    import grpc
    from google.protobuf.json_format import MessageToDict, ParseDict
except ImportError:  # pragma: no cover - fallback for REST-only installs
    grpc = None
    MessageToDict = None
    ParseDict = None


class LeadsServicePort(Protocol):
    async def create_lead_from_conversation(self, conversation_id: str, title: str, correlation_id: str) -> dict[str, object]: ...


class AnalyticsServicePort(Protocol):
    async def ingest_event(self, event: EventEnvelope) -> dict[str, object]: ...


class LeadsRestClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def create_lead_from_conversation(self, conversation_id: str, title: str, correlation_id: str) -> dict[str, object]:
        payload = LeadsCreateLeadFromConversationRequest(
            conversation_id=conversation_id,
            title=title,
            correlation_id=correlation_id,
        )
        async with httpx.AsyncClient(base_url=self._base_url, timeout=10.0) as client:
            response = await client.post(SAGA_INTERNAL_LEADS_CREATE_FROM_CONVERSATION_PATH, json=payload.model_dump())
            response.raise_for_status()
            return response.json()


class AnalyticsRestClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def ingest_event(self, event: EventEnvelope) -> dict[str, object]:
        payload = AnalyticsIngestEventRequest.model_validate(event.model_dump(mode="json"))
        async with httpx.AsyncClient(base_url=self._base_url, timeout=10.0) as client:
            response = await client.post(SAGA_INTERNAL_ANALYTICS_INGEST_EVENT_PATH, json=payload.model_dump())
            response.raise_for_status()
            return response.json()


class LeadsGrpcClient:
    def __init__(self, target: str) -> None:
        self._target = target

    async def create_lead_from_conversation(self, conversation_id: str, title: str, correlation_id: str) -> dict[str, object]:
        if grpc is None or MessageToDict is None:
            raise RuntimeError("gRPC support is not installed")
        lead_grpc = importlib.import_module("projects.optimalleads.leads.presentation.grpc.lead_internal_service_pb2")
        lead_grpc_api = importlib.import_module("projects.optimalleads.leads.presentation.grpc.lead_internal_service_pb2_grpc")

        request = lead_grpc.CreateLeadFromConversationRequest(
            conversation_id=conversation_id,
            title=title,
            correlation_id=correlation_id,
        )
        async with grpc.aio.insecure_channel(self._target) as channel:
            stub = lead_grpc_api.LeadsInternalServiceStub(channel)
            response = await stub.CreateLeadFromConversation(request)
        return MessageToDict(response, preserving_proto_field_name=True)


class AnalyticsGrpcClient:
    def __init__(self, target: str) -> None:
        self._target = target

    async def ingest_event(self, event: EventEnvelope) -> dict[str, object]:
        if grpc is None or MessageToDict is None or ParseDict is None:
            raise RuntimeError("gRPC support is not installed")
        analytics_grpc = importlib.import_module("projects.optimalleads.analytics.presentation.grpc.analytics_internal_service_pb2")
        analytics_grpc_api = importlib.import_module("projects.optimalleads.analytics.presentation.grpc.analytics_internal_service_pb2_grpc")

        request = analytics_grpc.IngestEventRequest()
        request.event_id = event.event_id
        request.aggregate_id = event.aggregate_id
        request.event_name = event.event_name
        request.event_kind = str(event.event_kind)
        request.correlation_id = event.correlation_id
        request.causation_id = event.causation_id or ""
        request.occurred_at = event.occurred_at or ""
        ParseDict(event.payload, request.payload)

        async with grpc.aio.insecure_channel(self._target) as channel:
            stub = analytics_grpc_api.AnalyticsInternalServiceStub(channel)
            response = await stub.IngestEvent(request)
        return MessageToDict(response, preserving_proto_field_name=True)


def build_leads_client(settings: SagaSettings) -> LeadsServicePort:
    if settings.internal_service_protocol == SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC:
        return LeadsGrpcClient(settings.leads_grpc_target)
    return LeadsRestClient(settings.leads_api_base_url)


def build_analytics_client(settings: SagaSettings) -> AnalyticsServicePort:
    if settings.internal_service_protocol == SAGA_INTERNAL_SERVICE_PROTOCOL_GRPC:
        return AnalyticsGrpcClient(settings.analytics_grpc_target)
    return AnalyticsRestClient(settings.analytics_api_base_url)