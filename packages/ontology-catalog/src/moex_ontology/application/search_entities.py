"""Search indexed ontology entities."""

from __future__ import annotations

from moex_ontology.domain.entity import OntologyEntity
from moex_ontology.ports.ontology_index import OntologyIndexPort
from moex_ontology.ports.ontology_provider import OntologyProviderPort


def search_entities(
    index: OntologyIndexPort,
    query: str,
    *,
    limit: int = 50,
    provider: OntologyProviderPort | None = None,
) -> list[OntologyEntity]:
    hits = index.search_entities(query, limit=limit)
    if hits or provider is None:
        return hits
    # Optional live provider fallback when index is empty for this query
    iris = provider.search(query, limit=limit)
    found: list[OntologyEntity] = []
    for iri in iris:
        ent = index.get_entity(iri)
        if ent is not None:
            found.append(ent)
    return found
