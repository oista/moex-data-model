"""Smoke test for Alembic 0007 doc_key coordinate migration (SQLite)."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

API_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = API_ROOT / "alembic.ini"
TRADING_COORDINATE = "moex:implementation:trading:1.0.0"


@pytest.mark.skipif(not ALEMBIC_INI.is_file(), reason="alembic.ini missing")
def test_0007_rewrites_legacy_trading_doc_key(tmp_path: Path) -> None:
    db_path = tmp_path / "mig.db"
    url = f"sqlite:///{db_path.as_posix()}"
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        # Minimal pre-0007 schema
        conn.execute(
            text(
                """
                CREATE TABLE workspace (
                    id VARCHAR(128) PRIMARY KEY,
                    name VARCHAR(256) NOT NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE workspace_document (
                    workspace_id VARCHAR(128) NOT NULL,
                    doc_key VARCHAR(64) NOT NULL,
                    content TEXT NOT NULL,
                    base_digest VARCHAR(128) NOT NULL DEFAULT '',
                    updated_by VARCHAR(128) NOT NULL DEFAULT 'dev',
                    PRIMARY KEY (workspace_id, doc_key),
                    FOREIGN KEY(workspace_id) REFERENCES workspace (id)
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE publication_request (
                    id VARCHAR(128) PRIMARY KEY,
                    workspace_id VARCHAR(128) NOT NULL,
                    implementation_id VARCHAR(256) NOT NULL,
                    doc_key VARCHAR(64) NOT NULL,
                    branch_name VARCHAR(256) NOT NULL,
                    base_revision VARCHAR(128) NOT NULL,
                    commit_sha VARCHAR(128) NOT NULL DEFAULT '',
                    review_url VARCHAR(512) NOT NULL DEFAULT '',
                    review_id VARCHAR(256) NOT NULL DEFAULT '',
                    status VARCHAR(64) NOT NULL,
                    actor VARCHAR(128) NOT NULL DEFAULT 'dev',
                    idempotency_key VARCHAR(256),
                    payload_fingerprint VARCHAR(128) NOT NULL DEFAULT '',
                    FOREIGN KEY(workspace_id) REFERENCES workspace (id)
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE diagram_layout (
                    diagram_id VARCHAR(256) PRIMARY KEY,
                    workspace_id VARCHAR(128) NOT NULL,
                    implementation_id VARCHAR(256) NOT NULL,
                    profile VARCHAR(32) NOT NULL,
                    model_revision VARCHAR(128) NOT NULL DEFAULT '',
                    nodes_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
        )
        conn.execute(
            text("INSERT INTO workspace (id, name) VALUES ('ws1', 'WS')")
        )
        conn.execute(
            text(
                "INSERT INTO workspace_document "
                "(workspace_id, doc_key, content) VALUES ('ws1', 'trading', 'x')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO publication_request "
                "(id, workspace_id, implementation_id, doc_key, branch_name, "
                "base_revision, status) "
                "VALUES ('pub1', 'ws1', :impl, 'trading', 'b', 'HEAD', 'submitted')"
            ),
            {"impl": TRADING_COORDINATE},
        )
        conn.execute(
            text(
                "INSERT INTO diagram_layout "
                "(diagram_id, workspace_id, implementation_id, profile) "
                "VALUES ('moex:diagram:ws1:logical', 'ws1', :impl, 'logical')"
            ),
            {"impl": TRADING_COORDINATE},
        )
        conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES ('0006_diagram_layout')")
        )

    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", url)
    cfg.set_main_option(
        "script_location", str(API_ROOT / "alembic")
    )
    command.upgrade(cfg, "0007_doc_key_coordinate")

    with engine.connect() as conn:
        doc = conn.execute(
            text("SELECT doc_key FROM workspace_document WHERE workspace_id='ws1'")
        ).scalar_one()
        assert doc == TRADING_COORDINATE
        pub = conn.execute(
            text("SELECT doc_key FROM publication_request WHERE id='pub1'")
        ).scalar_one()
        assert pub == TRADING_COORDINATE
        diagram_id = conn.execute(
            text("SELECT diagram_id FROM diagram_layout")
        ).scalar_one()
        assert TRADING_COORDINATE in diagram_id
        assert diagram_id.endswith(":logical")
