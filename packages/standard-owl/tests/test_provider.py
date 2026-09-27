"""OWLStandardProvider: distinct spec/impl bodies."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import ImplementationRef, SpecificationRef, StandardFamily

from moex_standard_owl.domain.body import OWLImplementationBody, OWLSpecificationBody
from moex_standard_owl.standard_provider import OWLStandardProvider

REPO = Path(__file__).resolve().parents[3]
FIBO_DESC = REPO / "model-assets" / "implementations" / "ontologies" / "fibo.yaml"
MINI_FIBO = Path(__file__).resolve().parent / "fixtures" / "mini_fibo"


def test_load_specification_and_implementation_are_distinct_types() -> None:
    provider = OWLStandardProvider()
    spec_ref = SpecificationRef(
        specification_id="moex:ontology:fibo",
        specification_version="master_2026Q2",
        specification_revision="master_2026Q2",
    )
    impl_ref = ImplementationRef(
        implementation_id="moex:owl:mini-fibo",
        implementation_revision="test",
    )
    spec = provider.load_specification_body(spec_ref, path=str(FIBO_DESC))
    impl = provider.load_implementation_body(impl_ref, path=str(MINI_FIBO))
    assert type(spec) is OWLSpecificationBody
    assert type(impl) is OWLImplementationBody
    assert type(spec) is not type(impl)
    assert provider.family is StandardFamily.OWL
    assert spec.ontology_id == "moex:ontology:fibo"


def test_enumerate_and_validate_mini_fibo() -> None:
    provider = OWLStandardProvider()
    impl_ref = ImplementationRef(
        implementation_id="moex:owl:mini-fibo",
        implementation_revision="test",
    )
    body = provider.load_implementation_body(impl_ref, path=str(MINI_FIBO))
    assert body.entity_count > 0
    elements = provider.enumerate_elements(body)
    assert any(e.kind.value == "ontology" for e in elements)
    assert any(e.kind.value == "class" for e in elements)
    diags = provider.validate_standard(body)
    # Broken fixture may produce warnings; no fatal required for empty reasoner
    assert all(d.severity.value != "fatal" for d in diags)
