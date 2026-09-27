"""workspace_document drafts

Revision ID: 0003_workspace_document
Revises: 0002_stage3_narrow
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_workspace_document"
down_revision: Union[str, Sequence[str], None] = "0002_stage3_narrow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace_document",
        sa.Column(
            "workspace_id",
            sa.String(length=128),
            sa.ForeignKey("workspace.id"),
            primary_key=True,
        ),
        sa.Column("doc_key", sa.String(length=64), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("base_digest", sa.String(length=128), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("workspace_document")
