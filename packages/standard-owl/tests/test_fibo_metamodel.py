"""FIBO profile metamodel load tests."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import SpecificationRef
from moex_standard_owl.domain.fibo_metamodel import (
    FiboSpecificationBody,
    load_fibo_specification_body,
)
from moex_standard_owl.domain.body import OWLSpecificationBody
from moex_standard_owl.standard_provider import OWLStandardProvider

REPO = Path(__file__).resolve().parents[3]
PROFILE = REPO / "model-assets" / "specifications" / "moex-fibo-profile" / "0.1"
FIBO_DESC = REPO / "model-assets" / "implementations" / "ontologies" / "fibo.yaml"


def test_load_fibo_specification_body_round_trip() -> None:
    body = load_fibo_specification_body(PROFILE)
    assert isinstance(body, FiboSpecificationBody)
    assert body.specification_id == "moex:specification:moex-fibo-profile:0.1"
    assert {d.code for d in body.domains} == {"FND", "BE"}
    assert any(m.id == "FND/DatesAndTimes" for m in body.modules)
    assert any(d.id == "BusinessDates" for d in body.documents)
    assert any(d.ontology_iri.endswith("BusinessDates/") for d in body.documents)
    assert any(a.annotation_property == "skos:definition" for a in body.annotation_requirements)
    assert any(p.id == "resource-iri" for p in body.iri_patterns)
    assert any(p.id == "fibo-prefix" for p in body.prefix_patterns)


def test_provider_loads_fibo_profile_as_fibo_body() -> None:
    provider = OWLStandardProvider()
    spec_ref = SpecificationRef(
        specification_id="moex:specification:moex-fibo-profile:0.1",
        specification_version="0.1.0",
        specification_revision="0.1.0",
    )
    body = provider.load_specification_body(
        spec_ref, path=str(PROFILE / "specification.yaml")
    )
    assert isinstance(body, FiboSpecificationBody)
    assert {d.code for d in body.domains} == {"FND", "BE"}


def test_provider_still_loads_release_descriptor_as_owl_body() -> None:
    provider = OWLStandardProvider()
    spec_ref = SpecificationRef(
        specification_id="moex:ontology:fibo",
        specification_version="master_2026Q2",
        specification_revision="master_2026Q2",
    )
    body = provider.load_specification_body(spec_ref, path=str(FIBO_DESC))
    assert isinstance(body, OWLSpecificationBody)
    assert body.ontology_id == "moex:ontology:fibo"
