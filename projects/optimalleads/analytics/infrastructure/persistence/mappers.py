from __future__ import annotations

import json

from projects.optimalleads.analytics.domain import Snapshot
from projects.optimalleads.analytics.infrastructure.persistence.models.projection import ProjectionRow


def snapshot_to_row(snapshot: Snapshot) -> ProjectionRow:
    return ProjectionRow(
        id="snapshot",
        name=json.dumps(
            {
                "conversations": {
                    conversation_id: {
                        "id": read_model.id,
                        "title": read_model.title,
                        "message_count": read_model.message_count,
                    }
                    for conversation_id, read_model in snapshot.conversations.items()
                },
                "leads": {
                    lead_id: {
                        "id": read_model.id,
                        "name": read_model.name,
                        "stage": read_model.stage,
                    }
                    for lead_id, read_model in snapshot.leads.items()
                },
            },
            ensure_ascii=True,
        ),
        category="snapshot",
    )


def row_to_snapshot(row: ProjectionRow) -> Snapshot:
    snapshot = Snapshot()

    try:
        payload = json.loads(row.name)
    except (TypeError, json.JSONDecodeError):
        return snapshot

    for conversation_id, conversation_data in payload.get("conversations", {}).items():
        snapshot.conversations[conversation_id] = snapshot.conversations.get(conversation_id) or snapshot.conversations.setdefault(
            conversation_id,
            snapshot.conversations.get(conversation_id) or None,
        )
        snapshot.conversations[conversation_id] = snapshot.conversations[conversation_id] or None

    snapshot.conversations.clear()
    for conversation_id, conversation_data in payload.get("conversations", {}).items():
        snapshot.register_conversation(
            str(conversation_data.get("id", conversation_id)),
            str(conversation_data.get("title", "")),
        )
        snapshot.conversations[conversation_id].message_count = int(conversation_data.get("message_count", 0))

    snapshot.leads.clear()
    for lead_id, lead_data in payload.get("leads", {}).items():
        snapshot.register_lead(
            str(lead_data.get("id", lead_id)),
            str(lead_data.get("name", "")),
        )
        snapshot.leads[lead_id].stage = str(lead_data.get("stage", "new"))

    return snapshot
