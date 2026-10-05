"""Assert mixin/enum OWL mapping conventions (ADR-030)."""

from __future__ import annotations

from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Namespace, URIRef

REPO_ROOT = Path(__file__).resolve().parents[3]
OWL_PATH = (
    REPO_ROOT / "generated" / "artifacts" / "moex-dams" / "0.1" / "moex-dams.owl.ttl"
)
DAMS = Namespace("https://data.moex.com/dams/")


def _graph() -> Graph:
    assert OWL_PATH.is_file(), f"missing committed OWL: {OWL_PATH}"
    g = Graph()
    g.parse(OWL_PATH, format="turtle")
    return g


def test_has_lifecycle_mixin_is_owl_class() -> None:
    g = _graph()
    assert (DAMS.HasLifecycle, RDF.type, OWL.Class) in g


def test_mixin_consumer_subclassof_has_lifecycle() -> None:
    g = _graph()
    consumers = list(g.subjects(RDFS.subClassOf, DAMS.HasLifecycle))
    assert consumers, "expected at least one class with rdfs:subClassOf HasLifecycle"


def test_enum_value_is_owl_class_with_fragment_iri() -> None:
    g = _graph()
    approved = URIRef("https://data.moex.com/dams/ApprovalStatusEnum#approved")
    assert (approved, RDF.type, OWL.Class) in g
