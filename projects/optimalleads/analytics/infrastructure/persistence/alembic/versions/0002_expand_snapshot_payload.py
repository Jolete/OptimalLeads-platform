from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_expand_snapshot_payload"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("projections", "name", existing_type=sa.String(length=200), type_=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    op.alter_column("projections", "name", existing_type=sa.Text(), type_=sa.String(length=200), existing_nullable=False)