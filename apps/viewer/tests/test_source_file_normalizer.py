"""Tests for type: source-file normalizer (Impl Артефакты cards)."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_publication_viewer.models.manifest_models import ManifestSection, SourceSpec
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.source_file_normalizer import SourceFileNormalizer

REPO = Path(__file__).resolve().parents[3]
MDM_BODY = (
    REPO
    / "model-assets"
    / "implementations"
    / "solutions"
    / "mdm"
    / "mdm-solution-model.yaml"
)


def test_normalize_solution_model_body() -> None:
    section = ManifestSection(
        id="artifact-model-body",
        title="Тело модели",
        description="Authored ModelPackage body.",
        type="source-file",
        kind="source",
        source=SourceSpec(format="yaml", path="mdm-solution-model.yaml"),
    )
    out = SourceFileNormalizer().normalize(section, MDM_BODY)
    assert out.type == "source-file"
    assert out.kind == "source"
    assert len(out.items) == 1
    item = out.items[0]
    assert item.id == "file:mdm-solution-model.yaml"
    assert item.title == "Тело модели"
    assert item.attributes["kind"] == "source_file"
    assert item.attributes["file_name"] == "mdm-solution-model.yaml"
    assert item.attributes["path"] == "mdm-solution-model.yaml"
    assert "mdm_solution_model" in item.attributes["text"]
    assert item.attributes["refs_out"] == []
    assert item.attributes["refs_in"] == []


def test_normalize_missing_file_raises(tmp_path: Path) -> None:
    section = ManifestSection(
        id="artifact-envelope",
        title="Конверт реализации",
        type="source-file",
        kind="source",
        source=SourceSpec(format="yaml", path="missing.yaml"),
    )
    with pytest.raises(NormalizeError, match="not found"):
        SourceFileNormalizer().normalize(section, tmp_path / "missing.yaml")


def test_repo_mdm_compiles_artifact_source_file_sections() -> None:
    from moex_publication_viewer.build import compile_modules

    modules = compile_modules(REPO, enforce_publication_contract=False)
    mdm = next(m for m in modules if m.module_id == "moex:module:mdm-solution")
    by_id = {s.id: s for s in mdm.sections}
    assert "artifact-model-body" in by_id
    assert "artifact-envelope" in by_id
    body = by_id["artifact-model-body"]
    assert body.type == "source-file"
    assert body.kind == "source"
    assert body.items[0].attributes.get("kind") == "source_file"
    assert body.items[0].attributes.get("file_name") == "mdm-solution-model.yaml"
    assert body.items[0].title == "Тело модели"
    env = by_id["artifact-envelope"]
    assert env.items[0].attributes.get("file_name") == "implementation.yaml"
