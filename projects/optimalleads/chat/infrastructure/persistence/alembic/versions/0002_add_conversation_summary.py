from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_conversation_summary"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chat_conversations", sa.Column("summary", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("chat_conversations", "summary")