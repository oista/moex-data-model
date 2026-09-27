"""SSSOM and LinkML mapping extractor tests."""

from __future__ import annotations

from pathlib import Path

from moex_semantic_mappings.linkml_extractor import extract_linkml_bindings
from moex_semantic_mappings.skos_glossary import load_skos_concept_scheme
from moex_semantic_mappings.sssom_adapter import load_sssom_yaml

REPO = Path(__file__).resolve().parents[3]
FIXTURE_SCHEMA = Path(__file__).parent / "fixtures" / "mapped_schema.yaml"
SSSOM = REPO / "model_src" / "mappings" / "dams-fibo.sssom.yaml"
SKOS = REPO / "model_src" / "glossary" / "skos_concepts.yaml"


def test_load_sssom_dams_fibo():
    ms = load_sssom_yaml(SSSOM)
    assert ms.mapping_set_id == "moex:mappings:dams-fibo"
    assert len(ms.mappings) == 1
    m = ms.mappings[0]
    assert m.subject.id == "dams:concept/Client"
    assert "LegalPerson" in m.object.id
    assert m.predicate == "skos:closeMatch"
    assert m.status == "approved"


def test_extract_linkml_bindings_from_fixture():
    bindings = extract_linkml_bindings(FIXTURE_SCHEMA)
    predicates = {b.predicate for b in bindings}
    assert "linkml:class_uri" in predicates
    assert "linkml:slot_uri" in predicates
    assert "linkml:meaning" in predicates
    assert "skos:closeMatch" in predicates or "skos:exactMatch" in predicates
    assert any(b.subject.kind == "linkml_enum_value" for b in bindings)


def test_skos_glossary_concepts():
    concepts = load_skos_concept_scheme(SKOS)
    assert len(concepts) >= 2
    client = next(c for c in concepts if c.id == "glossary:Client")
    assert client.pref_label
    assert "glossary:LegalEntity" in client.related
