"""Build OntologyEntityCard from index + provider + optional bindings."""

from __future__ import annotations

from moex_ontology.ports.ontology_index import OntologyIndexPort
from moex_ontology.ports.ontology_provider import OntologyProviderPort
from moex_ontology.ports.semantic_binding_repository import SemanticBindingRepositoryPort
from moex_ontology.read_models.entity_card import OntologyEntityCard
from moex_ontology.rdf_parser_local import curie_guess


def get_entity(
    index: OntologyIndexPort,
    iri: str,
    *,
    provider: OntologyProviderPort | None = None,
    bindings: SemanticBindingRepositoryPort | None = None,
) -> OntologyEntityCard | None:
    entity = index.get_entity(iri)
    if entity is None:
        return None

    parents: tuple[str, ...] = ()
    children: tuple[str, ...] = ()
    domain: tuple[str, ...] = ()
    range_: tuple[str, ...] = ()

    if provider is not None:
        parents = provider.parents(iri)
        children = provider.children(iri)
        domain_range = getattr(provider, "domain_range", None)
        if callable(domain_range):
            domain, range_ = domain_range(iri)
    else:
        rels = index.relations_for(iri, predicate="rdfs:subClassOf")
        parents = tuple(sorted({r.object for r in rels if r.subject == iri}))
        children = tuple(sorted({r.subject for r in rels if r.object == iri}))

    related_model: list = []
    related_glossary: list = []
    external: list = []
    if bindings is not None:
        for b in bindings.backlinks_for_ontology_entity(iri):
            if b.subject_kind in {"dams_element", "linkml_class", "linkml_slot", "linkml_enum_value"}:
                related_model.append(b)
            elif b.subject_kind == "glossary_term":
                related_glossary.append(b)
            else:
                external.append(b)
            if b.object_kind == "ontology_entity" and b.object_id != iri:
                external.append(b)

    return OntologyEntityCard(
        iri=entity.iri,
        curie=curie_guess(entity.iri),
        ontology_id=entity.ontology_id,
        kind=entity.kind,
        label=entity.label,
        definition=entity.definition,
        aliases=entity.alternative_labels,
        parents=parents,
        children=children,
        domain=domain,
        range=range_,
        deprecated=entity.deprecated,
        replaced_by=entity.replaced_by,
        related_model_elements=tuple(related_model),
        related_glossary_terms=tuple(related_glossary),
        external_mappings=tuple(external),
    )
