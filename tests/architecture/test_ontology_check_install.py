"""ontology-check must editable-install workspace packages with CLI extras."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "ontology-check.ps1"

# Local path deps declared by apps/cli (not on PyPI).
WORKSPACE_PACKAGES = (
    "packages/modeling-kernel",
    "packages/standard-linkml",
    "packages/specification-dams",
    "packages/publication",
    "packages/git-adapter",
    "packages/semantic-mappings",
    "packages/linkml-tooling",
    "packages/external-sources",
)


def test_ontology_check_installs_workspace_packages_with_cli_ontology() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "[ontology]" in text
    cli_extra = text.index("[ontology]")
    for rel in WORKSPACE_PACKAGES:
        assert rel in text, f"{SCRIPT.name} must install {rel} (local, not PyPI)"
        assert text.index(rel) < cli_extra, f"{rel} must appear before CLI [ontology] extra"
