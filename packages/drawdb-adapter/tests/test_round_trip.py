"""Golden round-trip and policy tests for drawdb-adapter."""

from __future__ import annotations

from moex_dams.projection.dbml import project_model_package_to_dbml

from moex_drawdb.domain import PatchOpKind, RejectCode
from moex_drawdb.parse import parse_dbml
from moex_drawdb.service import DrawDbProjectionService

MINI = {
    "element_id": "dams:model/mini/1.0.0",
    "name": "mini_model",
    "governance_classification": "internal",
    "conceptual_entities": [
        {"element_id": "dams:concept/mini/Client", "name": "ClientConcept"}
    ],
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
                    "multivalued": False,
                },
                {
                    "element_id": "dams:logical/mini/Client/fullName",
                    "name": "fullName",
                    "logical_type": "string",
                    "required": False,
                    "multivalued": False,
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
                    "multivalued": False,
                }
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
    "mappings": [
        {
            "element_id": "dams:map/mini/keep-me",
            "name": "cross_layer",
            "mapping_type": "field_mapping",
            "source_refs": ["dams:logical/mini/Client/clientId"],
            "target_refs": ["dams:physical/other"],
            "mapping_cardinality": "one_to_one",
        }
    ],
    "data_carriers": [
        {
            "element_id": "dams:physical/mini/client_tbl",
            "name": "client_tbl",
            "title": "Client table",
            "asset_kind": "relational_table",
            "physical_fields": [
                {
                    "element_id": "dams:physical/mini/client_tbl/client_id",
                    "name": "client_id",
                    "native_type": "varchar",
                    "required": True,
                    "carrier_ref": "dams:physical/mini/client_tbl",
                },
                {
                    "element_id": "dams:physical/mini/client_tbl/full_name",
                    "name": "full_name",
                    "native_type": "varchar",
                    "required": False,
                    "carrier_ref": "dams:physical/mini/client_tbl",
                },
            ],
        }
    ],
}


def test_parse_round_trip_tables() -> None:
    dbml = project_model_package_to_dbml(MINI, profile="logical")
    diagram = parse_dbml(dbml)
    names = {t.name for t in diagram.tables}
    assert "TradingClient" in names
    assert "Account" in names
    client = next(t for t in diagram.tables if t.name == "TradingClient")
    assert client.element_id == "dams:logical/mini/Client"
    assert any(c.element_id == "dams:logical/mini/Client/clientId" for c in client.columns)
    assert any(r.element_id == "dams:rel/mini/Account-Client" for r in diagram.refs)


def test_identity_round_trip_no_semantic_loss() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="logical")
    merged, patch = svc.from_dbml(MINI, dbml, profile="logical")
    assert not patch.rejected
    # element ids preserved
    ids = {e["element_id"] for e in merged["logical_entities"]}
    assert "dams:logical/mini/Client" in ids
    assert "dams:logical/mini/Account" in ids
    # non-projected metadata retained
    assert merged["governance_classification"] == "internal"
    assert merged["conceptual_entities"][0]["element_id"] == "dams:concept/mini/Client"
    assert any(m["element_id"] == "dams:map/mini/keep-me" for m in merged["mappings"])
    # relationship retained
    assert any(
        r["element_id"] == "dams:rel/mini/Account-Client"
        for r in merged.get("relationships") or []
    )


def test_add_attribute_produces_op() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="logical")
    # inject new column into TradingClient table body (after fullName column line)
    marker = "fullName string [note: 'dams:logical/mini/Client/fullName']"
    assert marker in dbml
    dbml2 = dbml.replace(
        marker,
        marker + "\n  nickname string",
        1,
    )
    _merged, patch = svc.from_dbml(MINI, dbml2, profile="logical")
    assert any(o.kind is PatchOpKind.ADD_ATTRIBUTE for o in patch.ops)


def test_reject_element_id_rewrite() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="logical")
    # strip element_id from TradingClient table note
    bad = dbml.replace(
        "element_id=dams:logical/mini/Client; Client",
        "Client",
        1,
    )
    _merged, patch = svc.from_dbml(MINI, bad, profile="logical")
    assert any(r.code is RejectCode.ELEMENT_ID_REWRITE for r in patch.rejected)


def test_conceptual_entities_survive_logical_apply() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="logical")
    merged, patch = svc.from_dbml(MINI, dbml, profile="logical")
    assert not patch.rejected
    assert merged["conceptual_entities"][0]["element_id"] == "dams:concept/mini/Client"
    assert merged["conceptual_entities"][0]["name"] == "ClientConcept"


def test_physical_identity_round_trip() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="physical")
    assert "client_tbl" in dbml
    merged, patch = svc.from_dbml(MINI, dbml, profile="physical")
    assert not patch.rejected
    ids = {o["element_id"] for o in merged["data_carriers"]}
    assert "dams:physical/mini/client_tbl" in ids
    # conceptual layer untouched by physical apply
    assert merged["conceptual_entities"][0]["element_id"] == "dams:concept/mini/Client"
    assert any(
        e["element_id"] == "dams:logical/mini/Client"
        for e in merged["logical_entities"]
    )


def test_physical_add_field_produces_op() -> None:
    svc = DrawDbProjectionService()
    dbml = svc.to_dbml(MINI, profile="physical")
    marker = "full_name varchar [note: 'dams:physical/mini/client_tbl/full_name']"
    if marker not in dbml:
        # tolerate alternate note formatting from projector
        marker = "full_name"
        assert marker in dbml
        # inject after first full_name column occurrence inside table
        idx = dbml.find(marker)
        assert idx >= 0
        line_end = dbml.find("\n", idx)
        dbml2 = dbml[:line_end] + "\n  nickname varchar" + dbml[line_end:]
    else:
        dbml2 = dbml.replace(marker, marker + "\n  nickname varchar", 1)
    _merged, patch = svc.from_dbml(MINI, dbml2, profile="physical")
    assert any(o.kind is PatchOpKind.ADD_FIELD for o in patch.ops)
