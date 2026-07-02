from __future__ import annotations

from uuid import UUID
from projects.optimalleads.leads.domain import Lead, LeadId, LeadName, LeadStage
from projects.optimalleads.leads.infrastructure.persistence.models.lead import LeadRow


def lead_to_row(lead: Lead) -> LeadRow:
    return LeadRow(
        id=str(lead.id.value),
        name=lead.name.value,
        stage=lead.stage.value,
        notes=list(lead.notes),
    )


def row_to_lead(row: LeadRow) -> Lead:
    return Lead(
        id=LeadId.create(UUID(row.id)),
        name=LeadName.create(row.name),
        stage=LeadStage.create(row.stage),
        notes=list(getattr(row, "notes", []) or []),
    )

