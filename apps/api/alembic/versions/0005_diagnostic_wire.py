"""validation_diagnostic wire fields

Revision ID: 0005_diagnostic_wire
Revises: 0004_publication_request
Create Date: 2026-09-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_diagnostic_wire"
down_revision: Union[str, Sequence[str], None] = "0004_publication_request"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "validation_diagnostic",
        sa.Column("path", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "validation_diagnostic",
        sa.Column("element_id", sa.String(length=256), nullable=True),
    )
    op.add_column(
        "validation_diagnostic",
        sa.Column("source", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "validation_diagnostic",
        sa.Column("line", sa.Integer(), nullable=True),
    )
    op.add_column(
        "validation_diagnostic",
        sa.Column("suggestion", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("validation_diagnostic", "suggestion")
    op.drop_column("validation_diagnostic", "line")
    op.drop_column("validation_diagnostic", "source")
    op.drop_column("validation_diagnostic", "element_id")
    op.drop_column("validation_diagnostic", "path")
