from __future__ import annotations

from fastapi.testclient import TestClient

from projects.optimalleads.chat.main import create_app


def test_chat_conversation_lifecycle() -> None:
    client = TestClient(create_app())

    response = client.post("/conversations", json={"title": "Sales"})
    assert response.status_code == 200
    conversation = response.json()
    conversation_id = conversation["conversation_id"]

    response = client.get(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Sales"

    response = client.post(f"/conversations/{conversation_id}/messages", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["messages"] == ["Hello"]

    response = client.get("/conversations")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = client.delete(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
