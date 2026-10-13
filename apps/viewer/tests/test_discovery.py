"""Discovery tests (ADR-054: manifest-derived implementation publish paths)."""

from pathlib import Path

from moex_publication_viewer.discovery import (
    discover_implementation_publish_paths,
    discover_manifest_paths,
    implementation_publish_paths_via_rglob,
    rglob_publish_paths,
)

REPO = Path(__file__).resolve().parents[3]


def test_discover_finds_publish_yaml(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")

    found = discover_manifest_paths(tmp_path)
    assert len(found) == 1
    assert found[0].name == "publish.yaml"
    assert ".venv" not in found[0].parts


def test_implementation_publish_paths_match_rglob_on_real_repo() -> None:
    """Coincidence gate (ADR-054 D3): manifest-derived == rglob under implementations/."""
    derived = discover_implementation_publish_paths(REPO)
    assert derived is not None
    via_rglob = implementation_publish_paths_via_rglob(REPO)
    assert {p.resolve() for p in derived} == {p.resolve() for p in via_rglob}
    # All eight packages currently ship a publish.yaml sibling.
    assert len(derived) == 8


def test_discover_uses_manifest_for_implementations(tmp_path: Path) -> None:
    impl = tmp_path / "model-assets" / "implementations"
    pkg = impl / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "implementation.yaml").write_text(
        "id: moex:implementation:pkg:0.1\nbody_ref: body.yaml\n",
        encoding="utf-8",
    )
    (pkg / "body.yaml").write_text("element_id: dams:model/pkg\n", encoding="utf-8")
    (pkg / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    # Stray publish.yaml at implementations root must NOT be discovered via manifest.
    (impl / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    (impl / "manifest.yaml").write_text(
        "manifest_schema_version: 0.1.0\n"
        "repository_id: moex:repository:test\n"
        "documents:\n"
        "  - id: moex:implementation:pkg:0.1\n"
        "    kind: package\n"
        "    path: pkg/implementation.yaml\n"
        "    version: '0.1'\n"
        "    owner: '@moex/a'\n",
        encoding="utf-8",
    )
    # Spec module outside implementations/ still found via rglob.
    spec = tmp_path / "model-assets" / "specifications" / "demo"
    spec.mkdir(parents=True)
    (spec / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")

    found = discover_manifest_paths(tmp_path)
    rels = {p.relative_to(tmp_path).as_posix() for p in found}
    assert "model-assets/implementations/pkg/publish.yaml" in rels
    assert "model-assets/specifications/demo/publish.yaml" in rels
    assert "model-assets/implementations/publish.yaml" not in rels


def test_rglob_still_used_when_no_manifest(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    assert discover_manifest_paths(tmp_path) == rglob_publish_paths(tmp_path)
