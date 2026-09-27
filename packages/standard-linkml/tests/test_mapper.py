from __future__ import annotations

from pathlib import Path

import pytest

from moex_standard_linkml.ingest.mapper import MappingFailed, map_er_dictionary
from moex_standard_linkml.ingest.profile import load_profile
from moex_standard_linkml.ingest.workbook import load_workbook_tables


def test_map_fixture_er_dictionary(
    fixture_dir: Path, fixture_profile_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    tables = load_workbook_tables(fixture_dir, profile)
    result = map_er_dictionary(tables, profile)

    pkg = result.package
    assert pkg["name"] == "pilot_solution_model"
    assert pkg["solution_ref"] == "eam:solution/PILOT"
    assert len(pkg["conceptual_entities"]) == 2
    assert len(pkg["logical_entities"]) == 2
    assert len(pkg["domain_contexts"]) == 1
    assert len(pkg["relationships"]) == 1

    client = next(e for e in pkg["logical_entities"] if e["name"] == "Client")
    assert client["element_id"] == "dams:logical/pilot/Client"
    assert client["context_ref"] == "dams:context/pilot"
    assert client["key_attribute_refs"] == [
        "dams:logical/pilot/Client/clientId"
    ]
    client_id = next(a for a in client["attributes"] if a["name"] == "clientId")
    assert client_id["logical_type"] == "identifier"
    assert client_id["required"] is True

    trade = next(e for e in pkg["logical_entities"] if e["name"] == "Trade")
    qty = next(a for a in trade["attributes"] if a["name"] == "quantity")
    assert qty["logical_type"] == "decimal"
    trade_date = next(a for a in trade["attributes"] if a["name"] == "tradeDate")
    assert trade_date["logical_type"] == "date"
    assert trade_date["required"] is False

    rel = pkg["relationships"][0]
    assert rel["source_entity_ref"] == "dams:logical/pilot/Trade"
    assert rel["target_entity_ref"] == "dams:logical/pilot/Client"
    assert rel["source_min_cardinality"] == 0
    assert "source_max_cardinality" not in rel  # unbounded *
    assert rel["target_min_cardinality"] == 1
    assert rel["target_max_cardinality"] == 1
    assert rel["identifying"] is False


def test_unknown_entity_fails(
    fixture_dir: Path, fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "Entities.csv").write_text(
        "name,title,description\nClient,Client,A client\n",
        encoding="utf-8",
    )
    (bad / "Attributes.csv").write_text(
        "entity,name,title,description,type,required,pk\n"
        "Unknown,x,x,x,VARCHAR,true,false\n",
        encoding="utf-8",
    )
    tables = load_workbook_tables(bad, profile)
    with pytest.raises(MappingFailed, match="unknown entity"):
        map_er_dictionary(tables, profile)
