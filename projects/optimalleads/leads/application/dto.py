from __future__ import annotations

from dataclasses import dataclass

from core_domain import ValidationError
from projects.optimalleads.leads.domain import LeadId, LeadName, LeadStage


@dataclass(frozen=True)
class CreateLeadCommand:
    __command__ = True
    __query__ = False

    name: str
    correlation_id: str | None = None

    def validate(self) -> None:
        LeadName.create(self.name)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class UpdateLeadCommand:
    __command__ = True
    __query__ = False

    lead_id: str
    name: str
    stage: str | None = None
    correlation_id: str | None = None

    def validate(self) -> None:
        LeadId.create(self.lead_id)
        LeadName.create(self.name)
        if self.stage is not None:
            LeadStage.create(self.stage)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class AdvanceLeadStageCommand:
    __command__ = True
    __query__ = False

    lead_id: str
    stage: str
    correlation_id: str | None = None

    def validate(self) -> None:
        LeadId.create(self.lead_id)
        LeadStage.create(self.stage)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class DeleteLeadCommand:
    __command__ = True
    __query__ = False

    lead_id: str
    correlation_id: str | None = None

    def validate(self) -> None:
        LeadId.create(self.lead_id)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class GetLeadQuery:
    __command__ = False
    __query__ = True

    lead_id: str


@dataclass(frozen=True)
class ListLeadsQuery:
    __command__ = False
    __query__ = True