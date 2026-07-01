from __future__ import annotations

from projects.optimalleads.leads.infrastructure.persistence.models.lead import LeadRow


def get_leads_model_modules() -> tuple[type[LeadRow]]:
    return (LeadRow,)
