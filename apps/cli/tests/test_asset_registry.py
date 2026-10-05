"""FilesystemImplementationCatalog unit tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from moex_model_cli.asset_registry import (
    CatalogBuildError,
    FilesystemImplementationCatalog,
)
from moex_model_cli.bootstrap import find_repo_root
from moex_modeling import ImplementationNotFound

REQUIRED_SOLUTION_SLUGS = {"mdm", "ucd", "crm", "esed"}


def _write_repo_marker(root: Path) -> None:
    marker = (
        root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
        / "moex-dams.yaml"
    )
    marker.parent.mkdir(parents=True)
    marker.write_text("id: stub\n", encoding="utf-8")


@pytest.fixture(scope="module")
def catalog() -> FilesystemImplementationCatalog:
    return FilesystemImplementationCatalog(find_repo_root())


def test_list_includes_five_solutions(catalog: FilesystemImplementationCatalog) -> None:
    slugs = {a.slug for a in catalog.list()}
    assert REQUIRED_SOLUTION_SLUGS <= slugs
    assert len(catalog.list()) >= 5


def test_resolve_slug_equals_coordinate(
    catalog: FilesystemImplementationCatalog,
) -> None:
    by_slug = catalog.resolve("mdm")
    by_id = catalog.resolve("moex:implementation:mdm:0.1.0")
    assert by_slug.id == by_id.id == "moex:implementation:mdm:0.1.0"
    assert by_slug.slug == "mdm"
    assert by_slug.body_path.name == "mdm-solution-model.yaml"
    assert by_slug.publication_manifest_path is not None
    assert by_slug.publication_manifest_path.name == "publish.yaml"


def test_mdm_publication_manifest(
    catalog: FilesystemImplementationCatalog,
) -> None:
    mdm = catalog.resolve("mdm")
    assert mdm.id == "moex:implementation:mdm:0.1.0"
    assert mdm.publication_manifest_path is not None
    assert mdm.publication_manifest_path.is_file()


def test_load_body_and_schema(catalog: FilesystemImplementationCatalog) -> None:
    text = catalog.load_body("mdm")
    assert text.strip()
    schema = catalog.resolve_schema("mdm")
    assert schema.is_file()
    assert schema.name == "moex-dams.yaml"


def test_publication_target_relative(
    catalog: FilesystemImplementationCatalog,
) -> None:
    target = catalog.publication_target("mdm")
    assert target.repo_path.endswith("mdm-solution-model.yaml")
    assert not Path(target.repo_path).is_absolute()
    assert (catalog.root / target.repo_path).is_file()


def test_unknown_token(catalog: FilesystemImplementationCatalog) -> None:
    with pytest.raises(ImplementationNotFound):
        catalog.resolve("no-such-implementation")


def test_duplicate_slug_raises(tmp_path: Path) -> None:
    _write_repo_marker(tmp_path)
    impl_root = tmp_path / "model-assets" / "implementations" / "solutions"
    for folder, body_name, ver in (("a", "a.yaml", "1.0.0"), ("b", "b.yaml", "2.0.0")):
        d = impl_root / folder
        d.mkdir(parents=True)
        (d / body_name).write_text("id: body\n", encoding="utf-8")
        (d / "implementation.yaml").write_text(
            yaml.dump(
                {
                    "id": f"moex:implementation:dup:{ver}",
                    "name": folder,
                    "version": ver,
                    "implementation_kind": "linkml",
                    "implementation_profile": "dams-data-model",
                    "implementation_body": body_name,
                    "body_ref": body_name,
                }
            ),
            encoding="utf-8",
        )
    with pytest.raises(CatalogBuildError, match="duplicate implementation slug"):
        FilesystemImplementationCatalog(tmp_path)


def test_broken_envelope_skipped(tmp_path: Path) -> None:
    _write_repo_marker(tmp_path)
    d = tmp_path / "model-assets" / "implementations" / "solutions" / "ok"
    d.mkdir(parents=True)
    (d / "ok.yaml").write_text("id: body\n", encoding="utf-8")
    (d / "implementation.yaml").write_text(
        yaml.dump(
            {
                "id": "moex:implementation:ok:1.0.0",
                "name": "ok",
                "implementation_kind": "linkml",
                "implementation_body": "ok.yaml",
            }
        ),
        encoding="utf-8",
    )
    bad = tmp_path / "model-assets" / "implementations" / "solutions" / "bad"
    bad.mkdir(parents=True)
    (bad / "implementation.yaml").write_text("not: a valid id package\n", encoding="utf-8")
    catalog = FilesystemImplementationCatalog(tmp_path)
    assert [a.slug for a in catalog.list()] == ["ok"]


def test_body_escape_not_registered(tmp_path: Path) -> None:
    _write_repo_marker(tmp_path)
    outside = tmp_path.parent / f"outside-body-{tmp_path.name}.yaml"
    outside.write_text("id: leaked\n", encoding="utf-8")
    d = tmp_path / "model-assets" / "implementations" / "solutions" / "leak"
    d.mkdir(parents=True)
    rel = Path(os.path.relpath(outside, d)).as_posix()
    (d / "implementation.yaml").write_text(
        yaml.dump(
            {
                "id": "moex:implementation:leak:1.0.0",
                "name": "leak",
                "implementation_kind": "linkml",
                "implementation_body": rel,
            }
        ),
        encoding="utf-8",
    )
    try:
        cat = FilesystemImplementationCatalog(tmp_path)
        assert "leak" not in {a.slug for a in cat.list()}
    finally:
        outside.unlink(missing_ok=True)
