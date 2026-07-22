from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "optimalleads_saga_processed_events",
        sa.Column("event_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("saga_id", sa.String(length=64), nullable=False),
        sa.Column("event_name", sa.String(length=255), nullable=False),
        sa.Column("aggregate_id", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="received"),
        sa.Column("current_phase", sa.String(length=255), nullable=False, server_default="received"),
        sa.Column("completed_steps_json", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_optimalleads_saga_processed_events_saga_id", "optimalleads_saga_processed_events", ["saga_id"])
    op.create_index("ix_optimalleads_saga_processed_events_aggregate_id", "optimalleads_saga_processed_events", ["aggregate_id"])
    op.create_index("ix_optimalleads_saga_processed_events_correlation_id", "optimalleads_saga_processed_events", ["correlation_id"])

    op.create_table(
        "optimalleads_saga_event_attempts",
        sa.Column("attempt_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("saga_id", sa.String(length=64), nullable=False),
        sa.Column("event_name", sa.String(length=255), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("finished_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.create_index("ix_optimalleads_saga_event_attempts_event_id", "optimalleads_saga_event_attempts", ["event_id"])
    op.create_index("ix_optimalleads_saga_event_attempts_saga_id", "optimalleads_saga_event_attempts", ["saga_id"])


def downgrade() -> None:
    op.drop_index("ix_optimalleads_saga_event_attempts_saga_id", table_name="optimalleads_saga_event_attempts")
    op.drop_index("ix_optimalleads_saga_event_attempts_event_id", table_name="optimalleads_saga_event_attempts")
    op.drop_table("optimalleads_saga_event_attempts")

    op.drop_index("ix_optimalleads_saga_processed_events_correlation_id", table_name="optimalleads_saga_processed_events")
    op.drop_index("ix_optimalleads_saga_processed_events_aggregate_id", table_name="optimalleads_saga_processed_events")
    op.drop_index("ix_optimalleads_saga_processed_events_saga_id", table_name="optimalleads_saga_processed_events")
    op.drop_table("optimalleads_saga_processed_events")