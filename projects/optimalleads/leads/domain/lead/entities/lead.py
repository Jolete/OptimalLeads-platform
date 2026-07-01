from __future__ import annotations

from dataclasses import dataclass, field

from core_domain import AggregateRoot
from core_domain import ValidationError
from projects.optimalleads.leads.domain.lead.value_objects.lead_id import LeadId
from projects.optimalleads.leads.domain.lead.value_objects.lead_name import LeadName
from projects.optimalleads.leads.domain.lead.value_objects.lead_stage import LeadStage


@dataclass
class Lead(AggregateRoot[LeadId]):
    id: LeadId
    name: LeadName
    stage: LeadStage = field(default_factory=lambda: LeadStage.create("new"))
    notes: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not isinstance(self.notes, list):
            raise ValidationError("Lead notes must be a list")

    def change_stage(self, new_stage: LeadStage) -> None:
        self.stage = new_stage
