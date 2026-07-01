from __future__ import annotations

from dataclasses import dataclass

from projects.optimalleads.leads.domain.lead.value_objects.lead_id import LeadId
from projects.optimalleads.leads.domain.lead.value_objects.lead_name import LeadName


@dataclass(frozen=True)
class LeadCreated:
    lead_id: LeadId
    name: LeadName
