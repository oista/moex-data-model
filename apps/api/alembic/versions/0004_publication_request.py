"""publication_request

Revision ID: 0004_publication_request
Revises: 0003_workspace_document
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_publication_request"
down_revision: Union[str, Sequence[str], None] = "0003_workspace_document"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "publication_request",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.String(length=128),
            sa.ForeignKey("workspace.id"),
            nullable=False,
        ),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("doc_key", sa.String(length=64), nullable=False),
        sa.Column("branch_name", sa.String(length=256), nullable=False),
        sa.Column("base_revision", sa.String(length=128), nullable=False),
        sa.Column("commit_sha", sa.String(length=128), nullable=False),
        sa.Column("review_url", sa.String(length=512), nullable=False),
        sa.Column("review_id", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=256), unique=True, nullable=True),
        sa.Column("payload_fingerprint", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("publication_request")
