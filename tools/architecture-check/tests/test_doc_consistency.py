from __future__ import annotations

from pathlib import Path

from architecture_check.doc_consistency import (
    check_docs,
    check_normative_unique,
    parse_frontmatter,
    schema_tree_root,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS = REPO_ROOT / "docs" / "architecture"
DAMS = REPO_ROOT / "model_src" / "schemas" / "moex-dams.yaml"


def test_real_docs_pass_consistency():
    assert check_docs(DOCS, DAMS) == []


def test_exactly_one_normative_document():
    assert check_normative_unique(DOCS) == []


def test_dams_tree_root_is_moex_model_repository():
    assert schema_tree_root(DAMS) == "MOEXModelRepository"


def test_missing_frontmatter_detected(tmp_path: Path):
    (tmp_path / "no_meta.md").write_text("# Hi\n", encoding="utf-8")
    (tmp_path / "ok.md").write_text(
        "---\nstatus: Draft\nversion: '0.1'\nnormative: true\n"
        "supersedes: []\nsuperseded_by: null\n---\n\n# Ok\n",
        encoding="utf-8",
    )
    errors = check_normative_unique(tmp_path)
    assert any("missing YAML frontmatter" in e for e in errors)


def test_parse_frontmatter_roundtrip():
    text = (
        "---\nstatus: Proposed\nversion: '0.2'\nnormative: true\n"
        "supersedes: []\nsuperseded_by: null\n---\n\n# Body\n"
    )
    meta, body = parse_frontmatter(text)
    assert meta is not None
    assert meta["normative"] is True
    assert body.startswith("# Body")
