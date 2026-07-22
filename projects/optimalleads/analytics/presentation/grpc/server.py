from __future__ import annotations

import logging
import importlib
from typing import TYPE_CHECKING, Any

try:
    import grpc  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency in REST-only environments
    grpc = None

if TYPE_CHECKING:
    import grpc as grpc_type  # type: ignore[import-not-found]

from core_domain import EventEnvelope, EventKind
from projects.optimalleads.analytics.application.dto import IngestEventCommand
from projects.optimalleads.analytics.infrastructure.persistence.bootstrap import get_analytics_runtime

from . import analytics_internal_service_pb2, analytics_internal_service_pb2_grpc

logger = logging.getLogger(__name__)


class AnalyticsInternalService(analytics_internal_service_pb2_grpc.AnalyticsInternalServiceServicer):
    async def IngestEvent(self, request: Any, context: Any):
        if grpc is None:
            raise RuntimeError("gRPC support is not installed")

        json_format = importlib.import_module("google.protobuf.json_format")

        runtime = await get_analytics_runtime()
        if runtime.mediator is None:
            await context.abort(grpc.StatusCode.UNAVAILABLE, "CQRS mediator is not available")

        payload = json_format.MessageToDict(request.payload, preserving_proto_field_name=True)

        event = EventEnvelope(
            event_id=request.event_id,
            aggregate_id=request.aggregate_id,
            event_name=request.event_name,
            event_kind=EventKind(request.event_kind),
            correlation_id=request.correlation_id,
            causation_id=request.causation_id or None,
            occurred_at=request.occurred_at or None,
            payload=payload,
        )
        await runtime.mediator.send(IngestEventCommand(event=event))
        return analytics_internal_service_pb2.IngestEventResponse(status="ingested")


async def create_grpc_server(host: str, port: int) -> "grpc_type.aio.Server":
    if grpc is None:
        raise RuntimeError("gRPC support is not installed")

    server = grpc.aio.server()
    analytics_internal_service_pb2_grpc.add_AnalyticsInternalServiceServicer_to_server(AnalyticsInternalService(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    logger.info("analytics.grpc.started", extra={"host": host, "port": port})
    return server