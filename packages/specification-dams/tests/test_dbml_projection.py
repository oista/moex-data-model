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
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Client/fullName",
                    "name": "fullName",
                    "data_type_ref": "dams:datatype/string",
                    "required": False,
                },
            ],
        },
        {
            "element_id": "dams:logical/mini/Account",
            "name": "Account",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Account/accountId",
                    "name": "accountId",
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Account/clientId",
                    "name": "clientId",
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
            ],
        },
    ],
    "relationships": [
        {
            "element_id": "dams:rel/mini/Account-Client",
            "name": "Account_owned_by_Client",
            "source_entity_ref": "dams:logical/mini/Account",
            "target_entity_ref": "dams:logical/mini/Client",
        }
    ],
    "data_carriers": [
        {
            "element_id": "dams:physical/mini/client-topic",
            "name": "client_changed_topic",
            "asset_kind": "stream_topic",
            "structure_ref": "dams:structure/mini/client-topic",
        },
        {
            "element_id": "dams:physical/mini/account_table",
            "name": "account",
            "asset_kind": "relational_table",
            "structure_ref": "dams:structure/mini/account",
        },
        {
            "element_id": "dams:physical/mini/client_table",
            "name": "client",
            "asset_kind": "relational_table",
            "structure_ref": "dams:structure/mini/client",
        },
    ],
    "data_structures": [
        {
            "element_id": "dams:structure/mini/client-topic",
            "name": "client_changed_topic",
            "schema_format": "relational",
            "root_local_key": "root",
            "nodes": [
                {
                    "local_key": "root",
                    "node_kind": "object",
                    "children": ["client_id"],
                },
                {
                    "local_key": "client_id",
                    "node_kind": "scalar",
                    "native_name": "client_id",
                    "native_type": "string",
                    "required": True,
                },
            ],
        },
        {
            "element_id": "dams:structure/mini/account",
            "name": "account",
            "schema_format": "relational",
            "root_local_key": "root",
            "nodes": [
                {
                    "local_key": "root",
                    "node_kind": "object",
                    "children": ["id", "client_id"],
                },
                {
                    "local_key": "id",
                    "node_kind": "scalar",
                    "native_name": "id",
                    "native_type": "uuid",
                    "required": True,
                },
                {
                    "local_key": "client_id",
                    "node_kind": "scalar",
                    "native_name": "client_id",
                    "native_type": "uuid",
                    "required": True,
                },
            ],
        },
        {
            "element_id": "dams:structure/mini/client",
            "name": "client",
            "schema_format": "relational",
            "root_local_key": "root",
            "nodes": [
                {
                    "local_key": "root",
                    "node_kind": "object",
                    "children": ["id"],
                },
                {
                    "local_key": "id",
                    "node_kind": "scalar",
                    "native_name": "id",
                    "native_type": "uuid",
                    "required": True,
                },
            ],
        },
    ],
    "mappings": [
        {
            "mapping_type": "field_mapping",
            "source_refs": ["dams:logical/mini/Client/clientId"],
            "target_refs": ["dams:structure/mini/client-topic#client_id"],
        },
        {
            "element_id": "dams:map/mini/account-client-fk",
            "name": "account_client_fk",
            "mapping_type": "field_mapping",
            "source_refs": ["dams:structure/mini/account#client_id"],
            "target_refs": ["dams:structure/mini/client#id"],
        },
    ],
}


def test_logical_profile_emits_table_and_columns() -> None:
    text = project_model_package_to_dbml(MINI, profile="logical")
    assert "Table TradingClient" in text
    assert "headercolor: #4285F4" in text
    assert "clientId identifier [not null" in text
    assert "fullName string" in text
    assert "Ref Account_owned_by_Client:" in text
    assert "element_id=dams:rel/mini/Account-Client" in text
    # cross-layer mapping has only one end in logical index → no field Ref
    assert "client_changed_topic" not in text


def test_physical_profile_notes_asset_kind() -> None:
    text = project_model_package_to_dbml(MINI, profile="physical")
    assert "Table client_changed_topic" in text
    assert "asset_kind=stream_topic" in text
    assert "headercolor: #0F9D58" in text
    assert "client_id string [not null" in text
    assert "Ref account_client_fk:" in text
    assert "account.client_id > client.id" in text
    assert "element_id=dams:map/mini/account-client-fk" in text


CONCEPTUAL_MINI = {
    "element_id": "dams:model/mini-conceptual/1.0.0",
    "name": "mini_conceptual",
    "conceptual_entities": [
        {
            "element_id": "dams:concept/Client",
            "name": "Client",
            "title": "Клиент",
        },
        {
            "element_id": "dams:concept/Account",
            "name": "Account",
            "title": "Счёт",
        },
    ],
    "relationships": [
        {
            "element_id": "dams:rel/mini/Account-Client",
            "name": "Account_owned_by_Client",
            "source_entity_ref": "dams:concept/Account",
            "target_entity_ref": "dams:concept/Client",
        }
    ],
}


def test_conceptual_profile_emits_marker_column_and_refs() -> None:
    text = project_model_package_to_dbml(CONCEPTUAL_MINI, profile="conceptual")
    assert "Table Client" in text
    assert "Table Account" in text
    assert "headercolor: #F4B400" in text
    assert "concept string [note: 'concept']" in text
    assert "Ref Account_owned_by_Client:" in text
    assert "Account.concept > Client.concept" in text
    assert "element_id=dams:rel/mini/Account-Client" in text


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
