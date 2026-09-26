"""Tests for FIBO discovery and aggregation."""

from pathlib import Path

from ontology.fibo.aggregation import aggregate_entities, filter_for_main_mart
from ontology.fibo.discovery import discover_rdf_files
from ontology.models import EntityOccurrence
from ontology.rdf_parser import parse_rdf_file

FIXTURES = Path(__file__).parent / "fixtures" / "mini_fibo"


def test_discovery_skips_exmp_and_root_about():
    files = discover_rdf_files(FIXTURES, ["FND", "BE"], include_examples=False)
    paths = [f.module_path for f in files]
    assert any(p.startswith("FND/") for p in paths)
    assert any(p.startswith("BE/") for p in paths)
    assert not any("EXMP" in p for p in paths)
    assert not any(p == "AboutFIBO.rdf" for p in paths)


def test_discovery_includes_examples_when_flagged():
    files = discover_rdf_files(FIXTURES, ["FND"], include_examples=True)
    paths = [f.module_path for f in files]
    assert any(p.startswith("EXMP/") for p in paths)


def test_discovery_finds_broken_file_under_fnd():
    files = discover_rdf_files(FIXTURES, ["FND"], include_examples=False)
    assert any(f.module_path.endswith("Broken.rdf") for f in files)


def test_aggregate_same_iri_across_modules():
    bd = FIXTURES / "FND" / "DatesAndTimes" / "BusinessDates.rdf"
    lp = FIXTURES / "BE" / "LegalEntities" / "LegalPersons.rdf"
    occs: list[EntityOccurrence] = []
    for path, module_path, domain in [
        (bd, "FND/DatesAndTimes/BusinessDates.rdf", "FND"),
        (lp, "BE/LegalEntities/LegalPersons.rdf", "BE"),
    ]:
        chunk, err = parse_rdf_file(
            path,
            module_path=module_path,
            source_release="master_2026Q2",
            source_domain=domain,
        )
        assert err is None
        occs.extend(chunk)

    aggregated = aggregate_entities(occs)
    business_days = [
        e
        for e in aggregated
        if e.local_name == "BusinessDay" and e.entity_type == "owl:Class"
    ]
    assert len(business_days) == 1
    ent = business_days[0]
    assert "FND/DatesAndTimes/BusinessDates.rdf" in (ent.module_path or "")
    assert "BE/LegalEntities/LegalPersons.rdf" in (ent.module_path or "")
    # Labels from both files merged
    assert "Business Day" in (ent.label or "")
    assert "Trading Day" in (ent.label or "")
    # Definitions merged
    assert ent.definition is not None
    assert "trading day" in ent.definition.lower() or "---" in ent.definition
    # Two SHAs
    assert " | " in ent.source_file_sha256


def test_filter_excludes_deprecated_by_default():
    occs, err = parse_rdf_file(
        FIXTURES / "FND" / "DatesAndTimes" / "BusinessDates.rdf",
        module_path="FND/DatesAndTimes/BusinessDates.rdf",
        source_release="master_2026Q2",
        source_domain="FND",
    )
    assert err is None
    aggregated = aggregate_entities(occs)
    main = filter_for_main_mart(
        aggregated,
        type_codes={"class", "object_property", "datatype_property", "annotation_property"},
        include_individuals=False,
        include_deprecated=False,
    )
    names = {e.local_name for e in main}
    assert "OldBusinessDay" not in names
    assert "BusinessDay" in names
    assert "Monday" not in names  # individual excluded


def test_filter_includes_individuals_when_requested():
    occs, err = parse_rdf_file(
        FIXTURES / "FND" / "DatesAndTimes" / "BusinessDates.rdf",
        module_path="FND/DatesAndTimes/BusinessDates.rdf",
        source_release="master_2026Q2",
        source_domain="FND",
    )
    assert err is None
    aggregated = aggregate_entities(occs)
    main = filter_for_main_mart(
        aggregated,
        type_codes={
            "class",
            "object_property",
            "datatype_property",
            "annotation_property",
            "individual",
        },
        include_individuals=True,
        include_deprecated=False,
    )
    assert any(e.local_name == "Monday" for e in main)
