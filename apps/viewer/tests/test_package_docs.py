"""Package documentation TOC + model ADR contract (ADR-028)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection, SourceSpec
from moex_publication_viewer.models.publication_models import (
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.package_docs import (
    PackageDocsNormalizer,
    validate_package_docs,
)
from moex_publication_viewer.publication_profiles import profile_spec
from moex_publication_viewer.build import impl_section_nav_children


def _toc(**overrides) -> dict:
    data = {
        "entry_for_agents": "consumer-context.md",
        "pages": [
            {
                "id": "consumer-context",
                "path": "consumer-context.md",
                "title": "Consumer context",
                "audience": "both",
                "role": "contract",
            }
        ],
    }
    data.update(overrides)
    return data


def _write_docs(root: Path, *, toc: dict | None = None, extra_files: dict[str, str] | None = None) -> Path:
    docs = root / "docs"
    docs.mkdir()
    (docs / "consumer-context.md").write_text(
        "# Consumer context\n\nPurpose: demo.\n", encoding="utf-8"
    )
    (docs / "toc.yaml").write_text(
        yaml.safe_dump(toc or _toc(), allow_unicode=True), encoding="utf-8"
    )
    for rel, text in (extra_files or {}).items():
        path = docs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return docs


def test_implementation_recommends_documentation():
    spec = profile_spec("implementation")
    assert spec is not None
    assert "documentation" in spec.recommended
    assert "documentation" not in spec.required


def test_manifest_accepts_documentation_kind():
    section = ManifestSection(
        id="documentation",
        title="Documentation",
        type="markdown-doc",
        kind="documentation",
        source=SourceSpec(format="yaml", path="docs/toc.yaml"),
    )
    assert section.kind == "documentation"


def test_validate_package_docs_ok(tmp_path: Path):
    docs = _write_docs(tmp_path)
    errors, warnings = validate_package_docs(docs)
    assert errors == []
    assert warnings == []


def test_validate_package_docs_requires_consumer_context(tmp_path: Path):
    docs = _write_docs(
        tmp_path,
        toc={
            "entry_for_agents": "notes.md",
            "pages": [
                {
                    "id": "notes",
                    "path": "notes.md",
                    "title": "Notes",
                    "audience": "human",
                    "role": "explanation",
                }
            ],
        },
        extra_files={"notes.md": "# Notes\n"},
    )
    (docs / "consumer-context.md").unlink()
    errors, _warnings = validate_package_docs(docs)
    assert any("consumer-context.md" in e for e in errors)


def test_validate_package_docs_missing_toc_path(tmp_path: Path):
    docs = _write_docs(
        tmp_path,
        toc=_toc(
            pages=[
                {
                    "id": "consumer-context",
                    "path": "consumer-context.md",
                    "title": "Consumer context",
                    "audience": "both",
                    "role": "contract",
                },
                {
                    "id": "missing",
                    "path": "gone.md",
                    "title": "Gone",
                    "audience": "human",
                    "role": "explanation",
                },
            ]
        ),
    )
    errors, _warnings = validate_package_docs(docs)
    assert any("gone.md" in e for e in errors)


def test_validate_package_docs_orphan_warning(tmp_path: Path):
    docs = _write_docs(tmp_path, extra_files={"extra.md": "# Extra\n"})
    errors, warnings = validate_package_docs(docs)
    assert errors == []
    assert any("extra.md" in w for w in warnings)


def test_validate_package_docs_adr_requires_template_and_toc(tmp_path: Path):
    docs = _write_docs(
        tmp_path,
        extra_files={"adr/0001-split.md": "# Split\nNo frontmatter.\n"},
    )
    errors, _warnings = validate_package_docs(docs)
    assert any("adr/0001-split.md" in e for e in errors)


def test_validate_package_docs_adr_ok(tmp_path: Path):
    adr = """---
id: trading-platform:adr:001
title: Demo vertical slice
date: 2026-10-04
status: accepted
model_revision: "1.0.0"
change_class: modeling
affects: []
supersedes: []
---

# Demo vertical slice

## Context
Need a first published slice.

## Decision
Publish trading-platform as the demo.

## Consequences
Consumers treat it as illustrative.
"""
    toc = _toc(
        pages=[
            {
                "id": "consumer-context",
                "path": "consumer-context.md",
                "title": "Consumer context",
                "audience": "both",
                "role": "contract",
            },
            {
                "id": "adr-001",
                "path": "adr/0001-demo-vertical-slice.md",
                "title": "Demo vertical slice",
                "audience": "both",
                "role": "decision",
            },
        ]
    )
    docs = _write_docs(
        tmp_path, toc=toc, extra_files={"adr/0001-demo-vertical-slice.md": adr}
    )
    errors, warnings = validate_package_docs(docs)
    assert errors == []
    assert warnings == []


def test_package_docs_normalizer_renders_entry_and_tree(tmp_path: Path):
    docs = _write_docs(tmp_path)
    section = ManifestSection(
        id="documentation",
        title="Documentation",
        type="markdown-doc",
        kind="documentation",
        source=SourceSpec(format="yaml", path="docs/toc.yaml"),
    )
    out = PackageDocsNormalizer().normalize(section, docs / "toc.yaml")
    assert out.kind == "documentation"
    assert "Consumer context" in (out.content or "")
    assert out.attributes.get("entry_for_agents") == "consumer-context.md"
    ids = [item.id for item in out.items]
    assert "consumer-context" in ids
    assert out.items[0].attributes.get("role") == "contract"
    assert out.items[0].attributes.get("content")


def test_package_docs_normalizer_fails_on_invalid_toc(tmp_path: Path):
    docs = _write_docs(
        tmp_path,
        toc=_toc(
            pages=[
                {
                    "id": "consumer-context",
                    "path": "consumer-context.md",
                    "title": "Consumer context",
                    "audience": "both",
                    "role": "contract",
                },
                {
                    "id": "missing",
                    "path": "gone.md",
                    "title": "Gone",
                    "audience": "human",
                    "role": "explanation",
                },
            ]
        ),
    )
    section = ManifestSection(
        id="documentation",
        title="Documentation",
        type="markdown-doc",
        kind="documentation",
        source=SourceSpec(format="yaml", path="docs/toc.yaml"),
    )
    with pytest.raises(NormalizeError):
        PackageDocsNormalizer().normalize(section, docs / "toc.yaml")


def test_group_solution_impl_nav_documentation_folder():
    sections = [
        PublicationSection(id="package", title="Package", type="key-value", kind="overview"),
        PublicationSection(id="conceptual", title="Conceptual entities", type="entity-table"),
        PublicationSection(id="logical", title="Logical entities", type="entity-table"),
        PublicationSection(id="logical-erd", title="Logical ER diagram", type="mermaid-diagram"),
        PublicationSection(id="physical", title="Physical objects", type="entity-table"),
        PublicationSection(id="physical-erd", title="Physical ER diagram", type="mermaid-diagram"),
        PublicationSection(id="slice-summary", title="Vertical slice summary", type="key-value"),
        PublicationSection(id="slice-nodes", title="Slice graph nodes", type="entity-table"),
        PublicationSection(
            id="slice-relations", title="Slice universe relations", type="entity-table"
        ),
        PublicationSection(
            id="model-assessment",
            title="Оценка соответствия требованиям модели",
            type="entity-table",
        ),
        PublicationSection(
            id="documentation",
            title="Documentation",
            type="markdown-doc",
            kind="documentation",
        ),
    ]
    kids = impl_section_nav_children(
        "trading-solution",
        PublicationModule(module_id="moex:module:trading-solution", title="T", sections=sections),
    )
    assert kids[-1].id == "implnav:trading-solution:group:documentation"
    assert kids[-1].title == "Documentation"
    assert [c.attributes["section_id"] for c in kids[-1].children] == ["documentation"]
    assert kids[-1].children[0].children == []
