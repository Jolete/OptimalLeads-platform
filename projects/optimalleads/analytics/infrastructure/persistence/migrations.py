from __future__ import annotations

from projects.optimalleads.analytics.infrastructure.persistence.models.projection import ProjectionRow


def get_analytics_model_modules() -> tuple[type[ProjectionRow]]:
    return (ProjectionRow,)
