"""Tests for ModelPackage → DBML projection."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.projection.dbml import (
    project_model_package_to_dbml,
    write_dbml_artifact,
)

MINI = {
    "element_id": "dams:model/mini/1.0.0",
    "name": "mini_model",
    "logical_entities": [
        {
            "element_id": "dams:logical/mini/Client",
            "name": "TradingClient",
            "title": "Client",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Client/clientId",
                    "name": "clientId",
                    "logical_type": "identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Client/fullName",
                    "name": "fullName",
                    "logical_type": "string",
                    "required": False,
                },
            ],
        }
    ],
    "physical_objects": [
        {
            "element_id": "dams:physical/mini/client-topic",
            "name": "client_changed_topic",
            "object_kind": "topic",
            "physical_fields": [
                {
                    "element_id": "dams:physical/mini/client-topic/client_id",
                    "name": "client_id",
                    "native_name": "client_id",
                    "native_type": "string",
                    "required": True,
                }
            ],
        }
    ],
    "mappings": [
        {
            "mapping_type": "field_mapping",
            "source_refs": ["dams:logical/mini/Client/clientId"],
            "target_refs": ["dams:physical/mini/client-topic/client_id"],
        }
    ],
}


def test_logical_profile_emits_table_and_columns() -> None:
    text = project_model_package_to_dbml(MINI, profile="logical")
    assert "Table TradingClient" in text
    assert "headercolor: #4285F4" in text
    assert "clientId identifier [not null" in text
    assert "fullName string" in text
    # cross-layer mapping has only one end in logical index → no Ref
    assert "Ref:" not in text


def test_physical_profile_notes_object_kind() -> None:
    text = project_model_package_to_dbml(MINI, profile="physical")
    assert "Table client_changed_topic" in text
    assert "object_kind=topic" in text
    assert "headercolor: #0F9D58" in text
    assert "client_id string [not null" in text


def test_write_dbml_artifact_writes_manifest(tmp_path: Path) -> None:
    src = tmp_path / "pkg.yaml"
    src.write_text(yaml.safe_dump(MINI), encoding="utf-8")
    out = tmp_path / "out.dbml"
    manifest = write_dbml_artifact(
        implementation_path=src,
        out_path=out,
        profile="logical",
    )
    assert out.is_file()
    assert "TradingClient" in out.read_text(encoding="utf-8")
    sidecar = out.with_name("out.dbml.manifest.json")
    assert sidecar.is_file()
    assert manifest.content_digest.startswith("sha256:")
    assert manifest.profile == "logical"
