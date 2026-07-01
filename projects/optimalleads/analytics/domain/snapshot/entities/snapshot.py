from __future__ import annotations

from dataclasses import dataclass, field

from core_domain import AggregateRoot
from projects.optimalleads.analytics.domain.snapshot.value_objects.snapshot_id import SnapshotId
from projects.optimalleads.analytics.domain.snapshot.entities.conversation_read_model import ConversationReadModel
from projects.optimalleads.analytics.domain.snapshot.entities.lead_read_model import LeadReadModel


@dataclass
class Snapshot(AggregateRoot[SnapshotId]):
    id: SnapshotId = field(default_factory=SnapshotId.create_unique)
    conversations: dict[str, ConversationReadModel] = field(default_factory=dict)
    leads: dict[str, LeadReadModel] = field(default_factory=dict)

    def register_conversation(self, conversation_id: str, title: str) -> None:
        self.conversations[conversation_id] = ConversationReadModel(id=conversation_id, title=title)

    def append_conversation_message(self, conversation_id: str) -> None:
        read_model = self.conversations.setdefault(conversation_id, ConversationReadModel(id=conversation_id, title=""))
        read_model.message_count += 1

    def register_lead(self, lead_id: str, name: str) -> None:
        self.leads[lead_id] = LeadReadModel(id=lead_id, name=name, stage="new")

    def change_lead_stage(self, lead_id: str, stage: str) -> None:
        read_model = self.leads.setdefault(lead_id, LeadReadModel(id=lead_id, name="", stage="new"))
        read_model.stage = stage
