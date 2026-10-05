"""Widen doc_key; rewrite legacy trading slug to coordinate; diagram_id format.

Revision ID: 0007_doc_key_coordinate
Revises: 0006_diagram_layout
Create Date: 2026-10-05
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_doc_key_coordinate"
down_revision: Union[str, Sequence[str], None] = "0006_diagram_layout"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Legacy Workbench slug → canonical coordinate (one-time data rewrite).
_TRADING_COORDINATE = "moex:implementation:trading:1.0.0"
_LEGACY_DOC_KEY = "trading"


def upgrade() -> None:
    # SQLite cannot ALTER COLUMN length meaningfully; recreate via batch where needed.
    with op.batch_alter_table("workspace_document") as batch:
        batch.alter_column(
            "doc_key",
            existing_type=sa.String(length=64),
            type_=sa.String(length=256),
            existing_nullable=False,
        )
    with op.batch_alter_table("publication_request") as batch:
        batch.alter_column(
            "doc_key",
            existing_type=sa.String(length=64),
            type_=sa.String(length=256),
            existing_nullable=False,
        )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE workspace_document SET doc_key = :new "
            "WHERE doc_key = :old"
        ),
        {"new": _TRADING_COORDINATE, "old": _LEGACY_DOC_KEY},
    )
    conn.execute(
        sa.text(
            "UPDATE publication_request SET doc_key = :new "
            "WHERE doc_key = :old"
        ),
        {"new": _TRADING_COORDINATE, "old": _LEGACY_DOC_KEY},
    )
    # Legacy diagram_id: moex:diagram:{workspace}:{profile}
    # → moex:diagram:{workspace}:{implementation_id}:{profile}
    rows = conn.execute(
        sa.text(
            "SELECT diagram_id, workspace_id, implementation_id, profile "
            "FROM diagram_layout"
        )
    ).mappings().all()
    for row in rows:
        old_id = row["diagram_id"]
        prefix = f"moex:diagram:{row['workspace_id']}:"
        if not old_id.startswith(prefix):
            continue
        rest = old_id[len(prefix) :]
        if rest.count(":") >= 1 and _TRADING_COORDINATE in old_id:
            continue
        # old form ends with profile only
        new_id = (
            f"moex:diagram:{row['workspace_id']}:"
            f"{row['implementation_id']}:{row['profile']}"
        )
        if new_id == old_id:
            continue
        conn.execute(
            sa.text(
                "UPDATE diagram_layout SET diagram_id = :new "
                "WHERE diagram_id = :old"
            ),
            {"new": new_id, "old": old_id},
        )
        conn.execute(
            sa.text(
                "UPDATE diagram_layout SET implementation_id = :impl "
                "WHERE diagram_id = :id AND "
                "(implementation_id IS NULL OR implementation_id = '' "
                "OR implementation_id = :legacy)"
            ),
            {
                "impl": _TRADING_COORDINATE,
                "id": new_id,
                "legacy": _LEGACY_DOC_KEY,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE workspace_document SET doc_key = :old "
            "WHERE doc_key = :new"
        ),
        {"new": _TRADING_COORDINATE, "old": _LEGACY_DOC_KEY},
    )
    conn.execute(
        sa.text(
            "UPDATE publication_request SET doc_key = :old "
            "WHERE doc_key = :new"
        ),
        {"new": _TRADING_COORDINATE, "old": _LEGACY_DOC_KEY},
    )
    with op.batch_alter_table("publication_request") as batch:
        batch.alter_column(
            "doc_key",
            existing_type=sa.String(length=256),
            type_=sa.String(length=64),
            existing_nullable=False,
        )
    with op.batch_alter_table("workspace_document") as batch:
        batch.alter_column(
            "doc_key",
            existing_type=sa.String(length=256),
            type_=sa.String(length=64),
            existing_nullable=False,
        )
