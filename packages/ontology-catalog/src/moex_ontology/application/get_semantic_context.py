"""Semantic neighborhood for an ontology entity."""

from __future__ import annotations

from moex_ontology.ports.semantic_binding_repository import SemanticBindingRepositoryPort
from moex_ontology.read_models.semantic_context import SemanticContext


def get_semantic_context(
    bindings: SemanticBindingRepositoryPort,
    entity_iri: str,
) -> SemanticContext:
    return SemanticContext(
        entity_iri=entity_iri,
        bindings=tuple(bindings.backlinks_for_ontology_entity(entity_iri)),
    )
