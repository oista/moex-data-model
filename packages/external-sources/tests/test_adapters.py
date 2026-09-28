"""Tests for registry / lockfile I/O and adapters."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_external_sources.factory import build_source, sync_source
from moex_external_sources.registry import (
    list_source_dirs,
    load_lockfile,
    load_registry,
)
from moex_external_sources.seeds import parse_seed_iris
from moex_modeling.external_sources.public import SourceKind

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_registry_and_seeds() -> None:
    reg = load_registry(FIXTURES / "fibo_source" / "registry.yaml")
    assert reg.source_id == "fibo"
    assert reg.kind == SourceKind.ONTOLOGY
    iris = parse_seed_iris(FIXTURES / "fibo_source" / "seeds" / "counterparty.txt")
    assert len(iris) == 1
    assert iris[0].endswith("LegalPerson")


def test_list_source_dirs(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "registry.yaml").write_text(
        "source_id: a\nkind: ontology\nadapter: fibo\nupstream_url: .\n",
        encoding="utf-8",
    )
    (tmp_path / "b").mkdir()
    assert [p.name for p in list_source_dirs(tmp_path)] == ["a"]


def test_fibo_sync_writes_module_and_lock(tmp_path: Path) -> None:
    import shutil

    src = tmp_path / "fibo"
    shutil.copytree(FIXTURES / "fibo_source", src)
    # Point upstream at absolute mini ontology
    registry_path = src / "registry.yaml"
    text = registry_path.read_text(encoding="utf-8")
    abs_up = (FIXTURES / "mini_ontology").resolve().as_posix()
    registry_path.write_text(
        text.replace("upstream_url: ../mini_ontology", f"upstream_url: {abs_up}"),
        encoding="utf-8",
    )

    artifact, entry, prev = sync_source(src, dry_run=False, write_lock=True)
    assert artifact.kind == SourceKind.ONTOLOGY
    assert entry.content_hash.startswith("sha256:")
    module = src / "modules" / "fibo-module.ttl"
    assert module.is_file()
    assert "LegalPerson" in module.read_text(encoding="utf-8")
    lock = load_lockfile(src / "lockfile.yaml")
    assert lock.lock.source_id == "fibo"
    assert prev is None

    # second sync → diff present (same digest → not breaking)
    _a2, _e2, prev2 = sync_source(src, dry_run=False, write_lock=True)
    assert prev2 is not None
    assert prev2.breaking is False


def test_git_artifact_sync(tmp_path: Path) -> None:
    import shutil

    src = tmp_path / "openapi"
    shutil.copytree(FIXTURES / "openapi_source", src)
    abs_up = (FIXTURES / "sample_spec_repo").resolve().as_posix()
    registry_path = src / "registry.yaml"
    text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        text.replace(
            "upstream_url: ../sample_spec_repo",
            f"upstream_url: {abs_up}",
        ),
        encoding="utf-8",
    )

    artifact, entry, _ = sync_source(src)
    assert artifact.kind == SourceKind.API_SPEC
    assert (src / "spec" / "openapi.yaml").is_file()
    assert entry.content_hash.startswith("sha256:")


def test_build_source_unknown_adapter(tmp_path: Path) -> None:
    (tmp_path / "registry.yaml").write_text(
        "source_id: x\nkind: ontology\nadapter: nope\nupstream_url: .\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown adapter"):
        build_source(tmp_path)
