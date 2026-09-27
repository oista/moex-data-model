"""core operational tables

Revision ID: 0001_core
Revises:
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_core"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_table(
        "model_revision_index",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("revision", sa.String(length=128), nullable=False),
        sa.Column("content_digest", sa.String(length=128), nullable=False),
    )
    op.create_table(
        "validation_run",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("overall_result", sa.String(length=64), nullable=False),
        sa.Column("reported_at", sa.String(length=64), nullable=False),
    )
    op.create_table(
        "validation_diagnostic",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "run_id",
            sa.String(length=128),
            sa.ForeignKey("validation_run.id"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
    )
    op.create_table(
        "audit_event",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_event")
    op.drop_table("validation_diagnostic")
    op.drop_table("validation_run")
    op.drop_table("model_revision_index")
    op.drop_table("workspace")
