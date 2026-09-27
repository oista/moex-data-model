"""RDFLib adapter smoke tests on mini_fibo."""

from __future__ import annotations

from pathlib import Path

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_standard_owl.provider import get_provider

FIXTURES = Path(__file__).parent / "fixtures" / "mini_fibo"
BUSINESS_DATES = (
    FIXTURES / "FND" / "DatesAndTimes" / "BusinessDates.rdf"
)


def test_rdflib_adapter_label_and_parents():
    adapter = RdflibOntologyAdapter.from_files([BUSINESS_DATES])
    iri = (
        "https://spec.edmcouncil.org/fibo/ontology/"
        "FND/DatesAndTimes/BusinessDates/BusinessDay"
    )
    assert adapter.label(iri) is not None
    assert adapter.definition(iri) is not None
    parents = adapter.parents(iri)
    assert any("OccurrenceKind" in p for p in parents)
    children = adapter.children(
        "https://spec.edmcouncil.org/fibo/ontology/"
        "FND/DatesAndTimes/Occurrences/OccurrenceKind"
    )
    assert any("BusinessDay" in c for c in children)


def test_search_finds_business_day():
    adapter = RdflibOntologyAdapter.from_directory(FIXTURES)
    hits = adapter.search("BusinessDay")
    assert any("BusinessDay" in h for h in hits)


def test_get_provider_falls_back_to_rdflib():
    provider = get_provider(FIXTURES, prefer_oak=False)
    entities = provider.entities()
    assert len(entities) > 0
