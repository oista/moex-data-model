"""Tests for ModelPackage → Mermaid erDiagram projection."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.projection.mermaid_er import (
    project_model_package_to_er_diagram,
    write_er_diagram_artifact,
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
                    "title": 'Name "quoted"',
                    "logical_type": "string",
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
                    "logical_type": "identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Account/clientId",
                    "name": "clientId",
                    "logical_type": "identifier",
                    "required": True,
                },
            ],
        },
        {
            "element_id": "dams:logical/mini/Contact",
            "name": "CONTACT",
            "title": "Контакт",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Contact/Id",
                    "name": "Id",
                    "logical_type": "identifier",
                    "required": True,
                },
            ],
        },
        {
            "element_id": "dams:logical/mini/Weird",
            "name": "9bad-name",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Weird/x",
                    "name": "x",
                    "logical_type": "string",
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
            "source_role": "clientId",
            "source_min_cardinality": 0,
            "source_max_cardinality": 999999,
            "target_min_cardinality": 0,
            "target_max_cardinality": 1,
        },
        {
            "element_id": "dams:rel/mini/hanging",
            "name": "Hanging",
            "source_entity_ref": "dams:logical/mini/Account",
            "target_entity_ref": "dams:logical/missing",
        },
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
        },
        {
            "element_id": "dams:physical/mini/account_table",
            "name": "account",
            "object_kind": "table",
            "physical_fields": [
                {
                    "element_id": "dams:physical/mini/account/id",
                    "name": "id",
                    "native_name": "id",
                    "native_type": "uuid",
                    "required": True,
                },
                {
                    "element_id": "dams:physical/mini/account/client_id",
                    "name": "client_id",
                    "native_name": "client_id",
                    "native_type": "uuid",
                    "required": True,
                },
            ],
        },
        {
            "element_id": "dams:physical/mini/client_table",
            "name": "client",
            "object_kind": "table",
            "physical_fields": [
                {
                    "element_id": "dams:physical/mini/client/id",
                    "name": "id",
                    "native_name": "id",
                    "native_type": "uuid",
                    "required": True,
                }
            ],
        },
    ],
    "mappings": [
        {
            "mapping_type": "field_mapping",
            "source_refs": ["dams:logical/mini/Client/clientId"],
            "target_refs": ["dams:physical/mini/client-topic/client_id"],
        },
        {
            "element_id": "dams:map/mini/account-client-fk",
            "name": "account_client_fk",
            "mapping_type": "field_mapping",
            "source_refs": ["dams:physical/mini/account/client_id"],
            "target_refs": ["dams:physical/mini/client/id"],
        },
    ],
}


def test_logical_er_diagram_entities_and_edge() -> None:
    text = project_model_package_to_er_diagram(MINI, profile="logical")
    assert text.startswith("erDiagram")
    assert "TradingClient" in text
    assert 'TradingClient["Client"]' in text
    assert "identifier clientId PK" in text
    assert 'string fullName "Name \\"quoted\\""' in text
    assert "clientId FK" in text or "clientId PK,FK" in text
    assert "TradingClient" in text and "Account" in text
    assert "||--o{" in text or "|o--o{" in text
    assert "Account_owned_by_Client" in text
    assert 'CONTACT["Контакт"]' in text
    assert "t_9bad_name" in text
    assert "Hanging" not in text  # hanging FK skipped


def test_physical_er_diagram_objects_and_mapping() -> None:
    text = project_model_package_to_er_diagram(MINI, profile="physical")
    assert text.startswith("erDiagram")
    assert "client_changed_topic" in text
    assert "account" in text
    assert "client" in text
    assert "uuid client_id FK" in text or "client_id FK" in text
    assert "account_client_fk" in text
    assert "||--" in text or "}o--" in text or "|o--" in text


def test_write_er_diagram_artifact(tmp_path: Path) -> None:
    src = tmp_path / "pkg.yaml"
    src.write_text(yaml.safe_dump(MINI), encoding="utf-8")
    out = tmp_path / "logical.erd.md"
    manifest = write_er_diagram_artifact(
        implementation_path=src,
        out_md=out,
        profile="logical",
    )
    assert out.is_file()
    body = out.read_text(encoding="utf-8")
    assert "```mermaid" in body
    assert "erDiagram" in body
    assert manifest.content_digest.startswith("sha256:")
    assert manifest.profile == "logical"
