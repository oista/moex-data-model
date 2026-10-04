"""Manifest load and validation tests."""

from pathlib import Path

import pytest
import yaml

from moex_publication_viewer.manifest_loader import load_manifest, resolve_source_path
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.validators import (
    ValidationError,
    check_instance_of_classes,
    validate_manifests,
)


def _write_manifest(path: Path, data: dict) -> None:
    path.write_text(yaml.dump(data), encoding="utf-8")


def test_skip_non_publication_kind(tmp_path: Path):
    p = tmp_path / "publish.yaml"
    _write_manifest(p, {"module_id": "x", "kind": "other", "title": "X", "sections": []})
    assert load_manifest(p) is None


def test_load_valid_manifest(tmp_path: Path):
    src = tmp_path / "data.csv"
    src.write_text("id,name\n1,a\n", encoding="utf-8")
    p = tmp_path / "publish.yaml"
    _write_manifest(
        p,
        {
            "module_id": "moex:module:demo",
            "kind": "publication_module",
            "title": "Demo",
            "version": 1,
            "sections": [
                {
                    "id": "t",
                    "title": "T",
                    "type": "entity-table",
                    "source": {"format": "csv", "path": "data.csv"},
                }
            ],
        },
    )
    m = load_manifest(p)
    assert m is not None
    assert m.version == "1"
    assert resolve_source_path(p, "data.csv") == src.resolve()


def test_duplicate_module_id(tmp_path: Path):
    src = tmp_path / "data.csv"
    src.write_text("id\n1\n", encoding="utf-8")
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    data = {
        "module_id": "same",
        "kind": "publication_module",
        "title": "A",
        "sections": [
            {
                "id": "t",
                "title": "T",
                "type": "entity-table",
                "source": {"format": "csv", "path": "../data.csv"},
            }
        ],
    }
    _write_manifest(a / "publish.yaml", data)
    _write_manifest(b / "publish.yaml", {**data, "title": "B"})
    from moex_publication_viewer.manifest_loader import load_manifest as lm

    pairs = [
        (a / "publish.yaml", lm(a / "publish.yaml")),
        (b / "publish.yaml", lm(b / "publish.yaml")),
    ]
    with pytest.raises(ValidationError) as exc:
        validate_manifests(pairs)
    assert "duplicate module_id" in str(exc.value)


def test_missing_source_path(tmp_path: Path):
    p = tmp_path / "publish.yaml"
    _write_manifest(
        p,
        {
            "module_id": "m",
            "kind": "publication_module",
            "title": "M",
            "sections": [
                {
                    "id": "t",
                    "title": "T",
                    "type": "entity-table",
                    "source": {"format": "csv", "path": "missing.csv"},
                }
            ],
        },
    )
    m = load_manifest(p)
    with pytest.raises(ValidationError) as exc:
        validate_manifests([(p, m)])
    assert "missing source file" in str(exc.value)


def test_check_instance_of_unknown_class_warns():
    dams = PublicationModule(
        module_id="moex:module:dams",
        title="DAMS",
        sections=[
            PublicationSection(
                id="explorer",
                title="Explorer",
                type="explorer",
                items=[
                    PublicationItem(
                        id="LogicalEntity",
                        title="LogicalEntity",
                        attributes={"kind": "class"},
                    )
                ],
            )
        ],
    )
    impl = PublicationModule(
        module_id="moex:module:demo",
        title="Demo",
        manifest_path="demo/publish.yaml",
        sections=[
            PublicationSection(
                id="logical",
                title="Logical",
                type="entity-table",
                instance_of="NoSuchClass",
                items=[],
            ),
            PublicationSection(
                id="ok",
                title="OK",
                type="entity-table",
                instance_of="LogicalEntity",
                items=[],
            ),
        ],
    )
    warnings = check_instance_of_classes([dams, impl])
    assert any("NoSuchClass" in w for w in warnings)
    assert not any("LogicalEntity" in w and "not found" in w for w in warnings)
