from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from core_domain import EventEnvelope, EventKind
from core_infrastructure.drivers.sqlalchemy import SqlAlchemyOutboxRepository, SqlAlchemyRepository
from projects.optimalleads.leads.domain.lead.entities.lead import Lead
from projects.optimalleads.leads.domain.lead.value_objects.lead_id import LeadId
from projects.optimalleads.leads.domain.lead.value_objects.lead_name import LeadName
from projects.optimalleads.leads.domain.lead.value_objects.lead_stage import LeadStage
from projects.optimalleads.leads.infrastructure.persistence.memory import MemoryLeadRepository, MemoryLeadsOutbox
from projects.optimalleads.leads.infrastructure.persistence.models.lead import LeadRow
from projects.optimalleads.leads.infrastructure.persistence.models.outbox import LeadsOutboxRow


def build_leads_repository_factory(session_factory: Callable[[], object]) -> Callable[[], SqlAlchemyRepository[Lead, str]]:
    return lambda: SqlAlchemyRepository[
        Lead,
        str,
    ](
        session=session_factory(),
        model_type=LeadRow,
        entity_factory=lambda row: Lead(
            id=LeadId.create(UUID(row.id)),
            name=LeadName.create(row.name),
            stage=LeadStage.create(row.stage),
            notes=list(getattr(row, "notes", []) or []),
        ),
        model_factory=lambda lead: LeadRow(
            id=str(lead.id.value),
            name=lead.name.value,
            stage=lead.stage.value,
            notes=list(lead.notes),
        ),
        id_extractor=lambda row: row.id,
    )


def build_leads_outbox_factory(session: object) -> SqlAlchemyOutboxRepository[LeadsOutboxRow]:
    return SqlAlchemyOutboxRepository[
        LeadsOutboxRow,
    ](
        session=session,
        model_type=LeadsOutboxRow,
        row_factory=lambda event: LeadsOutboxRow(
            event_id=event.event_id,
            aggregate_id=event.aggregate_id,
            event_name=event.event_name,
            event_kind=event.event_kind.value,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            occurred_at=event.occurred_at,
            payload=event.payload,
        ),
        event_factory=lambda row: EventEnvelope(
            event_id=row.event_id,
            aggregate_id=row.aggregate_id,
            event_name=row.event_name,
            event_kind=EventKind(row.event_kind),
            correlation_id=row.correlation_id,
            causation_id=row.causation_id,
            occurred_at=row.occurred_at,
            payload=row.payload,
        ),
        auto_commit=False,
    )


def build_leads_memory_runtime() -> tuple[Callable[[], MemoryLeadRepository], MemoryLeadsOutbox]:
    return (lambda: MemoryLeadRepository(), MemoryLeadsOutbox())
