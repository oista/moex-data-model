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

    concepts = {c["name"]: c for c in pkg["conceptual_entities"]}
    assert "Client" in concepts
    assert concepts["Client"]["element_id"] == "dams:concept/Client"

    client = next(e for e in pkg["logical_entities"] if e["name"] == "TradingClient")
    assert client["element_id"] == "dams:logical/pilot/TradingClient"
    assert client["context_ref"] == "dams:context/pilot"
    assert client["conceptual_entity_refs"] == ["dams:concept/Client"]
    assert client["key_attribute_refs"] == [
        "dams:logical/pilot/TradingClient/clientId"
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
    assert rel["target_entity_ref"] == "dams:logical/pilot/TradingClient"
    assert rel["source_min_cardinality"] == 0
    assert "source_max_cardinality" not in rel  # unbounded *
    assert rel["target_min_cardinality"] == 1
    assert rel["target_max_cardinality"] == 1
    assert rel["identifying"] is False

    assert len(pkg["data_carriers"]) == 1
    phys = pkg["data_carriers"][0]
    assert phys["name"] == "client_changed_topic"
    assert phys["asset_kind"] == "stream_topic"
    assert phys["element_id"] == "dams:physical/pilot/client_changed_topic"
    assert len(phys["physical_fields"]) == 1
    assert phys["physical_fields"][0]["native_name"] == "client_id"
    assert phys["physical_fields"][0]["carrier_ref"] == phys["element_id"]
    assert not pkg.get("access_points")  # topic → data_carriers only

    assert len(pkg["mappings"]) == 1
    mapping = pkg["mappings"][0]
    assert mapping["source_refs"] == [
        "dams:logical/pilot/TradingClient/clientId"
    ]
    assert mapping["target_refs"] == [
        "dams:physical/pilot/client_changed_topic/client_id"
    ]
    assert mapping["mapping_type"] == "field_mapping"


def test_unknown_conceptual_ref_fails(
    fixture_dir: Path, fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    bad = tmp_path / "bad-concept"
    bad.mkdir()
    (bad / "Conceptual.csv").write_text(
        "name,title,description\nClient,Client,A client\n",
        encoding="utf-8",
    )
    (bad / "Entities.csv").write_text(
        "name,title,description,conceptual_ref\n"
        "TradingClient,Client,A client,UnknownConcept\n",
        encoding="utf-8",
    )
    (bad / "Attributes.csv").write_text(
        "entity,name,title,description,type,required,pk\n"
        "TradingClient,x,x,x,VARCHAR,true,false\n",
        encoding="utf-8",
    )
    tables = load_workbook_tables(bad, profile)
    with pytest.raises(MappingFailed, match="unknown conceptual_ref"):
        map_er_dictionary(tables, profile)


def test_compat_stub_without_conceptual_sheet(
    fixture_profile_path: Path, tmp_path: Path
) -> None:
    """No Conceptual sheet → 1:1 stub concepts from entity names."""
    profile = load_profile(fixture_profile_path)
    compat = tmp_path / "compat"
    compat.mkdir()
    (compat / "Entities.csv").write_text(
        "name,title,description\nClient,Клиент,A client\n",
        encoding="utf-8",
    )
    (compat / "Attributes.csv").write_text(
        "entity,name,title,description,type,required,pk\n"
        "Client,clientId,Id,Id,UUID,true,true\n",
        encoding="utf-8",
    )
    tables = load_workbook_tables(compat, profile)
    assert any("Conceptual" in w and "not found" in w for w in tables.warnings)
    result = map_er_dictionary(tables, profile)
    pkg = result.package
    assert len(pkg["conceptual_entities"]) == 1
    assert pkg["conceptual_entities"][0]["element_id"] == "dams:concept/Client"
    logical = pkg["logical_entities"][0]
    assert logical["name"] == "Client"
    assert logical["conceptual_entity_refs"] == ["dams:concept/Client"]


def test_empty_conceptual_ref_with_sheet(
    fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    root = tmp_path / "empty-ref"
    root.mkdir()
    (root / "Conceptual.csv").write_text(
        "name,title,description\nClient,Client,A client\n",
        encoding="utf-8",
    )
    (root / "Entities.csv").write_text(
        "name,title,description,conceptual_ref\nOrphan,Orphan,No link,\n",
        encoding="utf-8",
    )
    (root / "Attributes.csv").write_text(
        "entity,name,title,description,type,required,pk\n"
        "Orphan,id,Id,Id,UUID,true,true\n",
        encoding="utf-8",
    )
    tables = load_workbook_tables(root, profile)
    result = map_er_dictionary(tables, profile)
    orphan = result.package["logical_entities"][0]
    assert orphan["conceptual_entity_refs"] == []
    assert len(result.package["conceptual_entities"]) == 1


def test_unknown_entity_fails(
    fixture_dir: Path, fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "Conceptual.csv").write_text(
        "name,title,description\nClient,Client,A client\n",
        encoding="utf-8",
    )
    (bad / "Entities.csv").write_text(
        "name,title,description,conceptual_ref\nClient,Client,A client,Client\n",
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


def test_unresolved_mapping_ref_fails(
    fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    root = tmp_path / "bad-map"
    root.mkdir()
    (root / "Conceptual.csv").write_text(
        "name,title,description\nClient,Client,A client\n",
        encoding="utf-8",
    )
    (root / "Entities.csv").write_text(
        "name,title,description,conceptual_ref\nClient,Client,A client,Client\n",
        encoding="utf-8",
    )
    (root / "Attributes.csv").write_text(
        "entity,name,title,description,type,required,pk\n"
        "Client,clientId,Id,Id,UUID,true,true\n",
        encoding="utf-8",
    )
    (root / "DataCarriers.csv").write_text(
        "name,title,description,asset_kind,qualified_name,technology,"
        "system_ref,direction,structure_ref\n"
        "t,t,topic desc,topic,q.n,Kafka,eam:system/X,outbound,"
        "https://example.com/schema\n",
        encoding="utf-8",
    )
    (root / "Mappings.csv").write_text(
        "name,source,target,mapping_type,mapping_cardinality\n"
        "m,Client.missing,t,field_mapping,one_to_one\n",
        encoding="utf-8",
    )
    tables = load_workbook_tables(root, profile)
    with pytest.raises(MappingFailed, match="unresolved source ref"):
        map_er_dictionary(tables, profile)
