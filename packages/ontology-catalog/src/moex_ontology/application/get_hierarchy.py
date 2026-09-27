"""Asserted hierarchy as OntologyTreeNode."""

from __future__ import annotations

from moex_ontology.ports.ontology_index import OntologyIndexPort
from moex_ontology.ports.ontology_provider import OntologyProviderPort
from moex_ontology.read_models.entity_card import OntologyTreeNode


def get_hierarchy(
    index: OntologyIndexPort,
    root_iri: str,
    *,
    predicate: str = "rdfs:subClassOf",
    provider: OntologyProviderPort | None = None,
    max_depth: int = 3,
) -> OntologyTreeNode | None:
    entity = index.get_entity(root_iri)
    has_children = False
    if provider is not None:
        has_children = bool(provider.children(root_iri, predicate=predicate))
    else:
        rels = index.relations_for(root_iri, predicate=predicate)
        has_children = any(r.object == root_iri for r in rels)
    if entity is None and not has_children:
        return None
    return _build_node(
        index,
        root_iri,
        provider=provider,
        predicate=predicate,
        depth=0,
        max_depth=max_depth,
        seen=set(),
    )


def _build_node(
    index: OntologyIndexPort,
    iri: str,
    *,
    provider: OntologyProviderPort | None,
    predicate: str,
    depth: int,
    max_depth: int,
    seen: set[str],
) -> OntologyTreeNode:
    entity = index.get_entity(iri)
    title = entity.label if entity else iri.rsplit("/", 1)[-1]
    description = entity.definition if entity else None
    attrs: dict[str, str | int | bool | None] = {
        "iri": iri,
        "kind": entity.kind if entity else None,
    }
    if depth >= max_depth or iri in seen:
        return OntologyTreeNode(id=iri, title=title, description=description, attributes=attrs)
    seen = set(seen)
    seen.add(iri)
    if provider is not None:
        child_iris = provider.children(iri, predicate=predicate)
    else:
        rels = index.relations_for(iri, predicate=predicate)
        child_iris = tuple(sorted({r.subject for r in rels if r.object == iri}))
    children = tuple(
        _build_node(
            index,
            child,
            provider=provider,
            predicate=predicate,
            depth=depth + 1,
            max_depth=max_depth,
            seen=seen,
        )
        for child in child_iris
    )
    return OntologyTreeNode(
        id=iri,
        title=title,
        description=description,
        children=children,
        attributes=attrs,
    )
