"""Tests for single-file RDF/OWL parsing."""

from pathlib import Path

import pytest

from ontology.rdf_parser import local_name_from_iri, parse_rdf_file

FIXTURES = Path(__file__).parent / "fixtures" / "mini_fibo"
BUSINESS_DATES = FIXTURES / "FND" / "DatesAndTimes" / "BusinessDates.rdf"
BROKEN = FIXTURES / "FND" / "Broken" / "Broken.rdf"


@pytest.fixture
def business_dates():
    occs, err = parse_rdf_file(
        BUSINESS_DATES,
        module_path="FND/DatesAndTimes/BusinessDates.rdf",
        source_release="master_2026Q2",
        source_domain="FND",
    )
    assert err is None
    return occs


def _by_local(occs, name: str):
    matches = [o for o in occs if o.local_name == name]
    assert matches, f"No entity with local_name={name}"
    return matches[0]


def test_extract_class_with_label_and_skos_definition(business_dates):
    ent = _by_local(business_dates, "BusinessDay")
    assert ent.entity_type == "owl:Class"
    assert ent.label == "Business Day"
    assert "financial markets" in (ent.definition or "")
    assert ent.label_language == "en"


def test_extract_object_property(business_dates):
    ent = _by_local(business_dates, "hasBusinessDayAdjustment")
    assert ent.entity_type == "owl:ObjectProperty"
    assert ent.label == "has business day adjustment"
    assert ent.definition is not None


def test_english_label_preferred_over_russian(business_dates):
    ent = _by_local(business_dates, "BusinessDay")
    assert ent.label == "Business Day"
    assert "Рабочий" not in (ent.label or "")
    # Russian should appear in alternatives
    assert ent.alternative_labels is not None
    assert "Рабочий день" in ent.alternative_labels


def test_multiple_english_labels_joined(business_dates):
    ent = _by_local(business_dates, "CalendarPeriod")
    assert ent.label is not None
    assert "Calendar Period" in ent.label
    assert "Calendar Interval" in ent.label
    assert " | " in ent.label


def test_definition_fallback_dcterms_description(business_dates):
    ent = _by_local(business_dates, "SettlementDay")
    assert ent.definition == "A day on which a settlement may occur."


def test_definition_fallback_scope_note(business_dates):
    ent = _by_local(business_dates, "ScopeOnlyThing")
    assert ent.definition == "Note used as definition fallback."


def test_no_definition_is_none(business_dates):
    ent = _by_local(business_dates, "UndocumentedThing")
    assert ent.definition is None


def test_deprecated_with_replacement(business_dates):
    ent = _by_local(business_dates, "OldBusinessDay")
    assert ent.is_deprecated is True
    assert ent.deprecated_replacement_iri is not None
    assert ent.deprecated_replacement_iri.endswith("/BusinessDay")


def test_superclasses_skip_blank_nodes(business_dates):
    ent = _by_local(business_dates, "BusinessDay")
    assert ent.superclasses is not None
    assert "OccurrenceKind" in ent.superclasses
    # blank-node restriction must not appear
    assert "restriction" not in ent.superclasses.lower()
    assert "_:" not in ent.superclasses


def test_local_name_from_hash_iri():
    assert local_name_from_iri("https://example.org/fibo#HashLocalName") == "HashLocalName"


def test_local_name_from_slash_iri():
    iri = "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/BusinessDay"
    assert local_name_from_iri(iri) == "BusinessDay"


def test_hash_local_name_entity(business_dates):
    ent = _by_local(business_dates, "HashLocalName")
    assert ent.iri.endswith("#HashLocalName")


def test_named_individual_extracted(business_dates):
    ent = _by_local(business_dates, "Monday")
    assert ent.entity_type == "owl:NamedIndividual"


def test_module_iri_and_sha(business_dates):
    ent = business_dates[0]
    assert ent.module_iri is not None
    assert "BusinessDates" in ent.module_iri
    assert len(ent.source_file_sha256) == 64
    assert ent.module_path == "FND/DatesAndTimes/BusinessDates.rdf"


def test_parse_error_on_broken_file():
    occs, err = parse_rdf_file(
        BROKEN,
        module_path="FND/Broken/Broken.rdf",
        source_release="master_2026Q2",
        source_domain="FND",
    )
    assert occs == []
    assert err is not None
    assert err.module_path == "FND/Broken/Broken.rdf"
    assert err.exception_type
    assert err.exception_message
