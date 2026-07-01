from __future__ import annotations

from dataclasses import dataclass

from projects.optimalleads.leads.domain.lead.value_objects.lead_id import LeadId
from projects.optimalleads.leads.domain.lead.value_objects.lead_stage import LeadStage


@dataclass(frozen=True)
class LeadStageChanged:
    lead_id: LeadId
    stage: LeadStage
