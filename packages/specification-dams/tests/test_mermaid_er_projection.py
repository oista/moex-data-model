"""Tests for ModelPackage → Mermaid erDiagram projection."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.projection.mermaid_er import (
    build_er_clickmap,
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
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Client/fullName",
                    "name": "fullName",
                    "title": 'Name "quoted"',
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
        {
            "element_id": "dams:logical/mini/Contact",
            "name": "CONTACT",
            "title": "Контакт",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Contact/Id",
                    "name": "Id",
                    "data_type_ref": "dams:datatype/identifier",
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
                    "data_type_ref": "dams:datatype/string",
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
    "data_carriers": [
        {
            "element_id": "dams:physical/mini/client-topic",
            "name": "client_changed_topic",
            "asset_kind": "stream_topic",
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
            "asset_kind": "relational_table",
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
            "asset_kind": "relational_table",
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


CONCEPTUAL_MINI = {
    "element_id": "dams:model/cdm-mini/1.0.0",
    "name": "cdm_mini",
    "conceptual_entities": [
        {
            "element_id": "dams:concept/LegalEntity",
            "name": "LegalEntity",
            "title": "Юридическое лицо",
        },
        {
            "element_id": "dams:concept/CorporateGroup",
            "name": "CorporateGroup",
            "title": "Группа компаний",
        },
    ],
    "relation_terms": [
        {
            "element_id": "dams:relterm/memberOf",
            "name": "memberOf",
            "forward_label": "является членом",
            "inverse_label": "включает",
        }
    ],
    "relationships": [
        {
            "element_id": "dams:rel/LegalEntity/memberOf",
            "name": "memberOf",
            "source_entity_ref": "dams:concept/LegalEntity",
            "target_entity_ref": "dams:concept/CorporateGroup",
            "relation_term_ref": "dams:relterm/memberOf",
            "term_direction": "forward",
            "source_min_cardinality": 0,
            "source_max_cardinality": 1,
            "target_min_cardinality": 0,
            "target_max_cardinality": 999,
        },
        {
            "element_id": "dams:rel/hanging",
            "name": "Hanging",
            "source_entity_ref": "dams:concept/LegalEntity",
            "target_entity_ref": "dams:concept/missing",
        },
    ],
}


def test_conceptual_er_diagram_entities_and_edge() -> None:
    text = project_model_package_to_er_diagram(CONCEPTUAL_MINI, profile="conceptual")
    assert text.startswith("erDiagram")
    assert 'LegalEntity["Юридическое лицо"]' in text
    assert 'CorporateGroup["Группа компаний"]' in text
    assert 'string concept "concept"' in text
    assert "является членом" in text
    assert "Hanging" not in text
    clickmap = build_er_clickmap(CONCEPTUAL_MINI, profile="conceptual")
    assert clickmap["entities"]["LegalEntity"]["element_id"] == "dams:concept/LegalEntity"
    assert clickmap["entities"]["LegalEntity"]["section_id"] == "conceptual"
    assert len(clickmap["edges"]) == 1
    assert clickmap["edges"][0]["element_id"] == "dams:rel/LegalEntity/memberOf"
    assert clickmap["edges"][0]["section_id"] == "relationships"
    assert clickmap["edges"][0]["label"] == "является членом"


def test_write_conceptual_er_diagram_writes_clickmap(tmp_path: Path) -> None:
    src = tmp_path / "pkg.yaml"
    src.write_text(yaml.safe_dump(CONCEPTUAL_MINI), encoding="utf-8")
    out = tmp_path / "conceptual.erd.md"
    manifest = write_er_diagram_artifact(
        implementation_path=src,
        out_md=out,
        profile="conceptual",
    )
    assert manifest.profile == "conceptual"
    clickmap_path = tmp_path / "conceptual.erd.clickmap.json"
    assert clickmap_path.is_file()
    clickmap = yaml.safe_load(clickmap_path.read_text(encoding="utf-8"))
    assert "LegalEntity" in clickmap["entities"]
