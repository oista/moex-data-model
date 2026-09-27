"""End-to-end build smoke tests."""

from pathlib import Path
import json

import pytest

from moex_publication_viewer.build import build
from moex_publication_viewer.validators import ValidationError


def test_build_tmp_repo(tmp_path: Path):
    (tmp_path / "mod").mkdir()
    (tmp_path / "mod" / "data.csv").write_text(
        "id,name,description\n1,Alpha,First\n", encoding="utf-8"
    )
    (tmp_path / "mod" / "publish.yaml").write_text(
        """
module_id: moex:module:tmp
kind: publication_module
title: Tmp
sections:
  - id: rows
    title: Rows
    type: entity-table
    source:
      format: csv
      path: data.csv
    columns: [id, name, description]
""",
        encoding="utf-8",
    )
    dist = tmp_path / "out"
    index = build(tmp_path, dist)
    html = index.read_text(encoding="utf-8")
    assert "moex:module:tmp" in html
    assert (dist / "viewer.css").is_file()
    assert (dist / "viewer.js").is_file()
    assert (dist / "manifest_registry.json").is_file()


def test_build_fails_on_missing_source(tmp_path: Path):
    (tmp_path / "mod").mkdir()
    (tmp_path / "mod" / "publish.yaml").write_text(
        """
module_id: moex:module:bad
kind: publication_module
title: Bad
sections:
  - id: rows
    title: Rows
    type: entity-table
    source:
      format: csv
      path: nope.csv
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        build(tmp_path, tmp_path / "out")


def test_repo_golden_three_modules():
    """Build against the real repository root (golden smoke)."""
    repo = Path(__file__).resolve().parents[2]
    dist = repo / "viewer" / "dist"
    index = build(repo, dist)
    html = index.read_text(encoding="utf-8")
    for module_id in (
        "moex:module:dams",
        "moex:module:fibo",
        "moex:module:trading-solution",
    ):
        assert module_id in html
    assert "LogicalEntity" in html
    assert '"type": "explorer"' in html or '"type":"explorer"' in html
    registry = json.loads((dist / "manifest_registry.json").read_text(encoding="utf-8"))
    ids = {m["module_id"] for m in registry["modules"]}
    assert ids == {
        "moex:module:dams",
        "moex:module:fibo",
        "moex:module:trading-solution",
    }
    dams = next(m for m in registry["modules"] if m["module_id"] == "moex:module:dams")
    assert "explorer" in dams["sections"]
