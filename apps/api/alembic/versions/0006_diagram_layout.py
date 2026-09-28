"""diagram_layout table

Revision ID: 0006_diagram_layout
Revises: 0005_diagnostic_wire
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_diagram_layout"
down_revision: Union[str, Sequence[str], None] = "0005_diagnostic_wire"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "diagram_layout",
        sa.Column("diagram_id", sa.String(length=256), primary_key=True),
        sa.Column(
            "workspace_id",
            sa.String(length=128),
            sa.ForeignKey("workspace.id"),
            nullable=False,
        ),
        sa.Column("implementation_id", sa.String(length=256), nullable=False),
        sa.Column("profile", sa.String(length=32), nullable=False),
        sa.Column("model_revision", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("nodes_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("diagram_layout")
