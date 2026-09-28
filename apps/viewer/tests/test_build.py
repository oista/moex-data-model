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
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
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
    assert '"tree_root": true' in html or '"tree_root":true' in html
    assert '"mixin": true' in html or '"mixin":true' in html
    assert "group:moex_core" in html or "group:moex-core" in html
    assert "structure_why" in html
    assert "anti-shadow-master" in html or "проекци" in html
    registry = json.loads((dist / "manifest_registry.json").read_text(encoding="utf-8"))
    ids = {m["module_id"] for m in registry["modules"]}
    assert {
        "moex:module:dams",
        "moex:module:fibo",
        "moex:module:trading-solution",
    }.issubset(ids)
    dams = next(m for m in registry["modules"] if m["module_id"] == "moex:module:dams")
    assert "explorer" in dams["sections"]
    fibo = next(m for m in registry["modules"] if m["module_id"] == "moex:module:fibo")
    assert "glossary" in fibo["sections"]
    assert "денежный поток" in html
    assert "FailureToPay" in html and "CreditEvent" in html

    catalog = registry.get("catalog")
    assert catalog is not None
    by_id = {n["id"]: n for n in catalog["nodes"]}
    assert by_id["trading-solution"]["conforms_to"] == "moex-dams"
    assert by_id["moex-dams"]["expressed_in"] == "LinkML"
    assert by_id["moex:ontology:fibo"]["role"] == "reference_specification"
    assert by_id["moex:ontology:fibo"].get("conforms_to") in (None, "")
    # Architecture catalog embedded; standards are labels only (no tree nodes)
    assert "architecture-catalog" in html
    assert '"role": "modeling_standard"' not in html
    assert '"role":"modeling_standard"' not in html
    js = (dist / "viewer.js").read_text(encoding="utf-8")
    assert "Implementations" in js
    assert "rootSpecifications" in js
    assert "navigateToNode" in js


def test_nav_group_children_hidden_overrides_display_flex():
    """display:flex on .nav-group-children must not defeat the hidden attribute."""
    css = (Path(__file__).resolve().parents[1] / "static" / "viewer.css").read_text(
        encoding="utf-8"
    )
    assert "display: flex" in css
    assert ".nav-group-children[hidden]" in css
    # Rule must set display:none so collapsed groups actually hide
    idx = css.index(".nav-group-children[hidden]")
    snippet = css[idx : idx + 80]
    assert "display: none" in snippet


def test_explorer_groups_selectable_cards_not_in_search_and_module_title():
    """Package groups open as cards; stay out of search index; module title is MOEX standart."""
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
    build(repo, dist)
    html = (dist / "index.html").read_text(encoding="utf-8")
    assert "MOEX standart" in html
    # Group ids must not appear as selectable search items
    assert '"item_id": "group:' not in html and '"item_id":"group:' not in html
    js = (repo / "apps" / "viewer" / "static" / "viewer.js").read_text(encoding="utf-8")
    assert "kind === \"group\"" in js or "kind === 'group'" in js
    assert "structure_why" in html
    # Collapsed-by-default: no auto-expand when openGroups is empty
    assert "openGroups.size === 0" not in js
    # Class-level expressed_in removed from LinkML explorer attributes
    # (catalog labels and slice TypedRelation edges may still use the word).
    pub = html.split('id="publication-data"', 1)[1].split("</script>", 1)[0]
    assert '"kind": "class"' in pub or '"kind":"class"' in pub
    assert '"kind": "group"' in pub or '"kind":"group"' in pub
    assert '"expressed_in":' not in pub and '"expressed_in" :' not in pub
