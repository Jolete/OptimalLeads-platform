from __future__ import annotations

from fastapi.testclient import TestClient

from projects.optimalleads.leads.main import create_app


def test_leads_crud_lifecycle() -> None:
    client = TestClient(create_app())

    response = client.post("/leads", json={"name": "Acme"})
    assert response.status_code == 200
    lead = response.json()
    lead_id = lead["lead_id"]

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Acme"

    response = client.get("/leads")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = client.put(f"/leads/{lead_id}", json={"name": "Acme Updated", "stage": "qualified"})
    assert response.status_code == 200
    assert response.json()["stage"] == "qualified"

    response = client.delete(f"/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
