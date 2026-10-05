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


def test_build_mermaid_diagram_section(tmp_path: Path):
    from moex_publication_viewer.assets import assert_no_required_cdn

    mod = tmp_path / "mod"
    pub = mod / "publications"
    pub.mkdir(parents=True)
    (pub / "logical.erd.md").write_text(
        "```mermaid\nerDiagram\n    Client {\n        string id PK\n    }\n```\n",
        encoding="utf-8",
    )
    (pub / "logical.erd.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>',
        encoding="utf-8",
    )
    (pub / "logical.dbml").write_text(
        "Table Client {\n  id string [not null]\n}\n",
        encoding="utf-8",
    )
    (mod / "publish.yaml").write_text(
        """
module_id: moex:module:erd-demo
kind: publication_module
title: ERD demo
profile: implementation
sections:
  - id: package
    title: Package
    kind: overview
    type: key-value
    source:
      format: yaml
      path: meta.yaml
  - id: logical-erd
    title: Logical ER diagram
    kind: classes
    type: mermaid-diagram
    source:
      format: markdown
      path: publications/logical.erd.md
  - id: conformance
    title: Conformance
    kind: conformance
    type: key-value
    source:
      format: yaml
      path: meta.yaml
""",
        encoding="utf-8",
    )
    (mod / "meta.yaml").write_text(
        "name: demo\nstatus: draft\n",
        encoding="utf-8",
    )
    dist = tmp_path / "out"
    index = build(tmp_path, dist)
    html = index.read_text(encoding="utf-8")
    assert "mermaid-diagram" in html
    assert "erDiagram" in html
    assert "<svg" in html
    assert "Table Client" in html
    assert "dbml_source" in html
    js = (dist / "viewer.js").read_text(encoding="utf-8")
    assert "renderMermaidDiagram" in js
    assert "function renderErdScene" in js
    assert 'data-erd-tab", "dbml"' in js or 'textContent = "DBML"' in js
    assert_no_required_cdn(html)


def test_repo_golden_three_modules():
    """Build against the real repository root (golden smoke)."""
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
    index = build(repo, dist)
    html = index.read_text(encoding="utf-8")
    for module_id in (
        "moex:module:dams",
        "moex:module:dsp",
        "moex:module:fibo",
        "moex:module:fibo-profile",
        "moex:module:mdm-solution",
    ):
        assert module_id in html
    assert "LogicalEntity" in html
    assert '"type": "explorer"' in html or '"type":"explorer"' in html
    assert '"tree_root": true' in html or '"tree_root":true' in html
    assert '"mixin": true' in html or '"mixin":true' in html
    assert "group:moex_core" in html or "group:moex-core" in html
    assert "group:overview" in html
    assert "group:classes" in html
    assert "group:spec-files" in html
    assert "group:implementations" in html
    assert "section:classes" in html
    assert '"kind": "section_ref"' in html or '"kind":"section_ref"' in html
    assert "file:specification.yaml" in html
    assert '"kind": "source_file"' in html or '"kind":"source_file"' in html
    assert '"kind": "implementation_ref"' in html or '"kind":"implementation_ref"' in html
    assert "renderYamlFold" in (dist / "viewer.js").read_text(encoding="utf-8")
    assert "structure_why" in html
    assert "anti-shadow-master" in html or "проекци" in html
    registry = json.loads((dist / "manifest_registry.json").read_text(encoding="utf-8"))
    ids = {m["module_id"] for m in registry["modules"]}
    assert {
        "moex:module:dams",
        "moex:module:fibo",
        "moex:module:fibo-profile",
        "moex:module:mdm-solution",
    }.issubset(ids)
    dams = next(m for m in registry["modules"] if m["module_id"] == "moex:module:dams")
    assert "explorer" in dams["sections"]
    fibo = next(m for m in registry["modules"] if m["module_id"] == "moex:module:fibo")
    assert "glossary" in fibo["sections"]
    assert "explorer" in fibo["sections"]
    assert "group:FND" in html or "group:BE" in html
    assert "денежный поток" in html
    assert "FailureToPay" in html and "CreditEvent" in html

    profile = next(m for m in registry["modules"] if m["module_id"] == "moex:module:fibo-profile")
    assert "explorer" in profile["sections"]
    assert profile.get("profile") == "ontology"
    assert "group:taxonomy" not in html
    assert "group:classes" in html
    assert "group:schema-files" in html
    assert "group:identity" in html
    assert "group:overview-glossary" in html
    assert '"id": "group:glossary"' not in html
    assert "group:overview" in html
    assert "group:fibo-domains" in html
    assert "group:fibo-patterns" in html
    assert "group:fibo-annotations" in html
    assert "group:fibo-metamodel" not in html
    assert "group:fibo-overview" not in html
    assert "domain:FND" in html
    assert "onto:BusinessDates" in html
    assert "AmountOfMoney" in html

    cat = next(m for m in registry["modules"] if "ontology-catalog" in m["module_id"])
    assert "explorer" in cat["sections"]
    assert "group:moex:ontology:fibo" in html
    assert "OccurrenceKind" in html

    catalog = registry.get("catalog")
    assert catalog is not None
    by_id = {n["id"]: n for n in catalog["nodes"]}
    assert by_id["mdm-solution"]["conforms_to"] == "moex-dams"
    assert by_id["moex-dams"]["expressed_in"] == "LinkML"
    assert by_id["moex-fibo-profile"]["role"] == "reference_specification"
    assert by_id["moex:ontology:fibo"]["role"] == "specification_implementation"
    assert by_id["moex:ontology:fibo"]["conforms_to"] == "moex-fibo-profile"
    # Architecture catalog embedded; standards are labels only (no tree nodes)
    assert "architecture-catalog" in html
    assert '"role": "modeling_standard"' not in html
    assert '"role":"modeling_standard"' not in html
    js = (dist / "viewer.js").read_text(encoding="utf-8")
    assert "Implementations" in js
    assert "rootSpecifications" in js
    assert "navigateToNode" in js
    assert "walkExplorerItems" in js
    assert "renderOntologyExplorerDetail" in js
    assert "appendCatalogNav" in js
    assert "nav-catalog-body" in js
    assert "nav-impl-children" not in js
    assert "makeCatalogBtn" not in js
    # Spec↔Impl only under explorer group:implementations (not catalog siblings)
    pub_raw = html.split('id="publication-data"', 1)[1].split(">", 1)[1].split(
        "</script>", 1
    )[0]
    pub_modules = json.loads(pub_raw)
    dams_pub = next(m for m in pub_modules if m["module_id"] == "moex:module:dams")
    dams_expl = next(s for s in dams_pub["sections"] if s["type"] == "explorer")
    impls_root = next(i for i in dams_expl["items"] if i["id"] == "group:implementations")
    top = impls_root.get("children") or []
    impl_ids = [c["id"] for c in top]
    assert impl_ids[0] == "implnav:glossary"
    assert impl_ids[1:3] == [
        "group:implementations-it-solutions",
        "group:implementations-projects",
    ]
    assert "moex-dsp" in impl_ids
    assert "moex-enterprise-conceptual-model" in impl_ids
    assert "moex-hierarchy" in impl_ids
    hierarchy = next(c for c in top if c["id"] == "moex-hierarchy")
    assert [c["title"] for c in hierarchy.get("children") or []] == [
        "Overview",
        "Entity hierarchy",
        "Артефакты",
    ]
    entity_nav = hierarchy["children"][1]
    assert (entity_nav.get("attributes") or {}).get("kind") == "section_ref"
    assert (entity_nav.get("attributes") or {}).get("section_id") == (
        "entity-hierarchy"
    )
    glossary_nav = top[0]
    assert (glossary_nav.get("attributes") or {}).get("section_id") == (
        "implementations-glossary"
    )
    assert any(s["id"] == "implementations-glossary" for s in dams_pub["sections"])
    projects = next(c for c in top if c["id"] == "group:implementations-projects")
    assert "client-accounts-csv-draft" in {c["id"] for c in projects.get("children") or []}
    it_sols = next(c for c in top if c["id"] == "group:implementations-it-solutions")
    assert {"mdm-solution", "ucd-solution", "crm-solution", "esed-solution"} <= {
        c["id"] for c in it_sols.get("children") or []
    }
    assert (projects.get("attributes") or {}).get("group_style") == "section_folder"
    assert (it_sols.get("attributes") or {}).get("group_style") == "section_folder"
    assert "renderImplTermDetail" in js
    assert "term_cards" in js
    assert by_id["moex-dams"].get("description")
    assert by_id["mdm-solution"].get("description")
    assert by_id["moex-fibo-profile"].get("description")


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
    """Package groups open as cards; stay out of search index; module title is moex.dams."""
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
    build(repo, dist)
    html = (dist / "index.html").read_text(encoding="utf-8")
    assert "moex.dams" in html
    assert "Data Specification Player" in html
    assert "data-ui=\"sidebar\"" in html or "data-ui='sidebar'" in html
    assert "data-viewer-version" in html
    assert "--brand:" in html or "--brand :" in html
    assert "font-family: \"MOEX UI\"" in html or "font-family:\"MOEX UI\"" in html or "MOEX UI" in html
    assert "moex.dsp" in html
    assert "edmc.fibo" in html
    # Group ids must not appear as selectable search items
    assert '"item_id": "group:' not in html and '"item_id":"group:' not in html
    js = (repo / "apps" / "viewer" / "static" / "viewer.js").read_text(encoding="utf-8")
    assert "kind === \"group\"" in js or "kind === 'group'" in js
    assert "groupBadge" in js or '?"ontology"' in js or "? \"ontology\"" in js
    assert "explore this module" in js
    assert "openSearchDialog" in js
    assert "structure_why" in html
    # Autonomous HTML: styles and script inlined
    assert "<style id=\"viewer-css\">" in html or "<style id='viewer-css'>" in html
    assert "<script id=\"viewer-js\">" in html or "<script id='viewer-js'>" in html
    assert 'href="viewer.css"' not in html
    assert 'src="viewer.js"' not in html
    assert "data:font/woff2;base64," in html
    # Collapsed-by-default: no auto-expand when openGroups is empty
    assert "openGroups.size === 0" not in js
    # Class-level expressed_in removed from LinkML explorer attributes
    # (catalog labels and slice TypedRelation edges may still use the word).
    pub = html.split('id="publication-data"', 1)[1].split("</script>", 1)[0]
    assert '"kind": "class"' in pub or '"kind":"class"' in pub
    assert '"kind": "group"' in pub or '"kind":"group"' in pub
    assert '"expressed_in":' not in pub and '"expressed_in" :' not in pub
