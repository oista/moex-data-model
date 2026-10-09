"""PR-C3: L2 invariant validators — valid pass, invalid emit DAMS-INV-* / tagged codes."""

from __future__ import annotations

from moex_modeling import DiagnosticSeverity

from moex_dams.rules.data_structure import check_data_structures
from moex_dams.rules.semantic_layer import check_semantic_layer
from moex_dams.rules.technical_assets import check_technical_assets


def _inv_ids(diags) -> set[str]:
    out: set[str] = set()
    for d in diags:
        for det in d.diagnostic_details or ():
            if det.detail_key == "invariant_id":
                out.add(str(det.detail_value))
        if d.diagnostic_code.startswith("DAMS-INV-"):
            out.add(d.diagnostic_code.replace("DAMS-", ""))
    return out


def test_inv_001_identifying_requires_is_identifying() -> None:
    """INV-001 invalid: property_kind=identifying without is_identifying=true."""
    bad = {
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/C",
                "name": "C",
                "description": "c",
                "lifecycle_status": "active",
            }
        ],
        "conceptual_properties": [
            {
                "element_id": "dams:concept/C/p",
                "name": "p",
                "description": "p",
                "lifecycle_status": "active",
                "property_owner_entity_ref": "dams:concept/C",
                "significance_basis": ["identifying"],
                "property_kind": "identifying",
                "genesis_kind": "native",
            }
        ],
    }
    diags = check_semantic_layer(bad)
    inv = [d for d in diags if d.diagnostic_code == "DAMS-INV-001"]
    assert inv, diags
    assert inv[0].severity == DiagnosticSeverity.ERROR
    assert "is_identifying" in inv[0].diagnostic_message
    assert "Remediation:" in inv[0].diagnostic_message

    good = {
        **bad,
        "conceptual_properties": [
            {
                **bad["conceptual_properties"][0],
                "is_identifying": True,
            }
        ],
    }
    assert "DAMS-INV-001" not in {d.diagnostic_code for d in check_semantic_layer(good)}


def test_inv_010_source_pointer_requires_artifact() -> None:
    """INV-010: slot text — pointer only inside source_artifact_ref."""
    base = {
        "element_id": "dams:model/x/1",
        "data_structures": [
            {
                "element_id": "dams:structure/x/T",
                "schema_format": "json_schema",
                "structure_version": "1.0.0",
                "root_local_key": "root",
                "source_pointer": "#/definitions/Foo",
                "nodes": [
                    {"local_key": "root", "node_kind": "object", "children": []},
                ],
            }
        ],
    }
    diags = check_data_structures(base)
    assert "DAMS-INV-010" in {d.diagnostic_code for d in diags}
    assert "INV-010" in _inv_ids(diags)

    base["data_structures"][0]["source_artifact_ref"] = "https://example.org/schema.json"
    assert "DAMS-INV-010" not in {
        d.diagnostic_code for d in check_data_structures(base)
    }


def test_inv_011_schema_dialect_format_family() -> None:
    """INV-011 mirrors LinkML rule; AsyncAPI divergence not widened here."""
    base = {
        "element_id": "dams:model/x/1",
        "data_structures": [
            {
                "element_id": "dams:structure/x/T",
                "schema_format": "avro",
                "schema_dialect": "https://example.org/dialect",
                "structure_version": "1.0.0",
                "root_local_key": "root",
                "nodes": [
                    {"local_key": "root", "node_kind": "object", "children": []},
                ],
            }
        ],
    }
    diags = check_data_structures(base)
    assert "DAMS-INV-011" in {d.diagnostic_code for d in diags}
    assert "AsyncAPI" in diags[0].diagnostic_message or any(
        "AsyncAPI" in (d.diagnostic_message or "") for d in diags
    )

    base["data_structures"][0]["schema_format"] = "json_schema"
    assert "DAMS-INV-011" not in {
        d.diagnostic_code for d in check_data_structures(base)
    }


def test_inv_014_reference_requires_target() -> None:
    """INV-014: slot text — reference_target for node_kind=reference."""
    base = {
        "element_id": "dams:model/x/1",
        "data_structures": [
            {
                "element_id": "dams:structure/x/T",
                "schema_format": "json_schema",
                "structure_version": "1.0.0",
                "root_local_key": "root",
                "nodes": [
                    {"local_key": "root", "node_kind": "object", "children": ["r"]},
                    {"local_key": "r", "node_kind": "reference"},
                ],
            }
        ],
    }
    diags = check_data_structures(base)
    assert "DAMS-INV-014" in {d.diagnostic_code for d in diags}

    base["data_structures"][0]["nodes"][1]["reference_target"] = "dams:structure/x/Other"
    assert "DAMS-INV-014" not in {
        d.diagnostic_code for d in check_data_structures(base)
    }


def test_inv_018_direction_forbidden_tagged() -> None:
    data = {
        "element_id": "dams:model/x/1",
        "data_containers": [
            {
                "element_id": "dams:container/x/db",
                "name": "db",
                "asset_kind": "database",
                "asset_namespace": "ns",
                "qualified_name": "db",
                "direction": "inbound",
            }
        ],
    }
    diags = check_technical_assets(data)
    assert "INV-018" in _inv_ids(diags)
