from __future__ import annotations

import logging

from typing import TYPE_CHECKING, Any

try:
    import grpc  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency in REST-only environments
    grpc = None

if TYPE_CHECKING:
    import grpc as grpc_type  # type: ignore[import-not-found]

from projects.optimalleads.leads.application.dto import CreateLeadCommand
from projects.optimalleads.leads.infrastructure.persistence.bootstrap import get_leads_runtime
from projects.optimalleads.leads.presentation.api.router import _serialize_lead

from . import lead_internal_service_pb2, lead_internal_service_pb2_grpc

logger = logging.getLogger(__name__)


class LeadsInternalService(lead_internal_service_pb2_grpc.LeadsInternalServiceServicer):
    async def CreateLeadFromConversation(self, request: Any, context: Any):
        if grpc is None:
            raise RuntimeError("gRPC support is not installed")

        runtime = await get_leads_runtime()
        if runtime.mediator is None:
            await context.abort(grpc.StatusCode.UNAVAILABLE, "CQRS mediator is not available")

        lead = await runtime.mediator.send(
            CreateLeadCommand(
                name=f"Lead from conversation: {request.title}",
                correlation_id=request.correlation_id or None,
            )
        )
        serialized = _serialize_lead(lead)
        return lead_internal_service_pb2.LeadResponse(
            id=str(serialized["id"]),
            name=str(serialized["name"]),
            stage=str(serialized["stage"]),
            notes=[str(note) for note in serialized["notes"]],
        )


async def create_grpc_server(host: str, port: int) -> "grpc_type.aio.Server":
    if grpc is None:
        raise RuntimeError("gRPC support is not installed")

    server = grpc.aio.server()
    lead_internal_service_pb2_grpc.add_LeadsInternalServiceServicer_to_server(LeadsInternalService(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    logger.info("leads.grpc.started", extra={"host": host, "port": port})
    return server