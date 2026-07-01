from __future__ import annotations

from fastapi.testclient import TestClient

from core_domain.contracts import EventEnvelope
from projects.optimalleads.analytics.main import create_app


def test_analytics_ingest_and_snapshot() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/analytics/ingest",
        json={
            "event_id": "evt-1",
            "aggregate_id": "lead-1",
            "event_name": "LeadCreated",
            "event_kind": "domain",
            "correlation_id": "corr-1",
            "causation_id": None,
            "occurred_at": "2026-07-01T00:00:00Z",
            "payload": {"lead_id": "lead-1", "name": "Acme"},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ingested"

    response = client.get("/analytics/snapshot")
    assert response.status_code == 200
    assert "leads" in response.json()
