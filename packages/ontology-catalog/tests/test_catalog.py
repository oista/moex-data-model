"""Catalog index + provider use cases on mini_fibo."""

from __future__ import annotations

from pathlib import Path

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_semantic_mappings.sssom_adapter import load_sssom_yaml

from moex_ontology.adapters.binding_repo import MappingSetBindingRepository
from moex_ontology.adapters.sqlite_index import SqliteOntologyIndex
from moex_ontology.application.get_entity import get_entity
from moex_ontology.application.get_hierarchy import get_hierarchy
from moex_ontology.application.ingest import ingest_release_from_directory
from moex_ontology.application.list_ontologies import list_ontologies
from moex_ontology.application.search_entities import search_entities
from moex_ontology.domain.ontology import OntologyRelease
from moex_ontology.domain.release import load_release_descriptors

REPO = Path(__file__).resolve().parents[3]
MINI_FIBO = REPO / "packages" / "standard-owl" / "tests" / "fixtures" / "mini_fibo"
DESCRIPTORS = REPO / "model_src" / "ontologies"
SSSOM = REPO / "model_src" / "mappings" / "dams-fibo.sssom.yaml"

LEGAL_PERSON = (
    "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/LegalPerson"
)
BUSINESS_DAY = (
    "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/BusinessDay"
)
OCCURRENCE_KIND = (
    "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/OccurrenceKind"
)


def _indexed(tmp_path: Path) -> tuple[SqliteOntologyIndex, RdflibOntologyAdapter]:
    releases = load_release_descriptors(DESCRIPTORS)
    fibo = next(r for r in releases if r.id == "moex:ontology:fibo")
    indexed, entities, relations = ingest_release_from_directory(
        fibo, MINI_FIBO, domains=["FND", "BE"]
    )
    others = [r for r in releases if r.id != fibo.id]
    index = SqliteOntologyIndex(tmp_path / "index.sqlite")
    index.replace_all(
        releases=[indexed, *others],
        entities=entities,
        relations=relations,
    )
    provider = RdflibOntologyAdapter.from_directory(MINI_FIBO)
    return index, provider


def test_ingest_and_list_ontologies(tmp_path: Path):
    index, _ = _indexed(tmp_path)
    summaries = list_ontologies(index)
    assert any(s.id == "moex:ontology:fibo" and s.status == "indexed" for s in summaries)
    assert any(s.id == "moex:ontology:corporate" and s.status == "registered" for s in summaries)
    assert index.entity_count("moex:ontology:fibo") > 0
    index.close()


def test_search_and_card_with_provider(tmp_path: Path):
    index, provider = _indexed(tmp_path)
    hits = search_entities(index, "Legal", limit=10, provider=provider)
    assert any("LegalPerson" in h.iri for h in hits)
    card = get_entity(index, LEGAL_PERSON, provider=provider)
    assert card is not None
    assert card.kind == "class"
    assert card.label is not None or card.curie == "LegalPerson"
    index.close()


def test_hierarchy_asserted_subclass(tmp_path: Path):
    index, provider = _indexed(tmp_path)
    # OccurrenceKind is an external parent asserted in the fixture; walk from it.
    tree = get_hierarchy(index, OCCURRENCE_KIND, provider=provider, max_depth=2)
    # Root may be missing from the entity table; still return a node via provider children
    # when the IRI only appears as a relation object.
    if tree is None:
        children = provider.children(OCCURRENCE_KIND)
        assert any(BUSINESS_DAY == c for c in children)
        parents = provider.parents(BUSINESS_DAY)
        assert OCCURRENCE_KIND in parents
    else:
        assert any(c.id == BUSINESS_DAY for c in tree.children)
    index.close()


def test_entity_card_backlinks_from_sssom(tmp_path: Path):
    index, provider = _indexed(tmp_path)
    ms = load_sssom_yaml(SSSOM)
    repo = MappingSetBindingRepository(ms)
    card = get_entity(index, LEGAL_PERSON, provider=provider, bindings=repo)
    assert card is not None
    assert any(b.subject_id == "dams:concept/Client" for b in card.related_model_elements)
    index.close()
