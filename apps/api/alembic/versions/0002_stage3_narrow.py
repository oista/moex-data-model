"""stage3 narrow-v2 tables

Revision ID: 0002_stage3_narrow
Revises: 0001_core
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_stage3_narrow"
down_revision: Union[str, Sequence[str], None] = "0001_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_identity",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("display_name", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_table(
        "role_binding",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("user_identity.id"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("user_id", "role", name="uq_role_binding"),
    )
    op.create_table(
        "workspace_member",
        sa.Column(
            "workspace_id",
            sa.String(length=128),
            sa.ForeignKey("workspace.id"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.String(length=128),
            sa.ForeignKey("user_identity.id"),
            primary_key=True,
        ),
        sa.Column("role", sa.String(length=64), nullable=False),
    )
    op.create_table(
        "generation_job",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.String(length=128),
            sa.ForeignKey("workspace.id"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("idempotency_key", sa.String(length=256), unique=True, nullable=True),
        sa.Column("payload_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("finished_at", sa.String(length=64), nullable=True),
    )
    op.create_table(
        "generated_artifact",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(length=128),
            sa.ForeignKey("generation_job.id"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("path_or_uri", sa.String(length=512), nullable=False),
        sa.Column("content_digest", sa.String(length=128), nullable=False),
    )
    op.create_table(
        "model_index",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("revision", sa.String(length=128), nullable=False),
        sa.Column("content_digest", sa.String(length=128), nullable=False),
        sa.Column("indexed_at", sa.String(length=64), nullable=False),
    )
    op.create_table(
        "model_element_index",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "index_id",
            sa.String(length=128),
            sa.ForeignKey("model_index.id"),
            nullable=False,
        ),
        sa.Column("element_id", sa.String(length=256), nullable=False),
        sa.Column("element_kind", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("layer", sa.String(length=64), nullable=False),
    )
    op.add_column(
        "validation_run",
        sa.Column("workspace_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "validation_run",
        sa.Column("job_id", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("validation_run", "job_id")
    op.drop_column("validation_run", "workspace_id")
    op.drop_table("model_element_index")
    op.drop_table("model_index")
    op.drop_table("generated_artifact")
    op.drop_table("generation_job")
    op.drop_table("workspace_member")
    op.drop_table("role_binding")
    op.drop_table("user_identity")
