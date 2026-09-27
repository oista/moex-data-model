"""Port: governed semantic bindings (SSSOM / LinkML mappings)."""

from __future__ import annotations

from typing import Protocol

from moex_ontology.read_models.semantic_context import SemanticBindingView


class SemanticBindingRepositoryPort(Protocol):
    def list_bindings(
        self,
        *,
        subject_id: str | None = None,
        object_id: str | None = None,
        mapping_set_id: str | None = None,
    ) -> list[SemanticBindingView]: ...

    def backlinks_for_ontology_entity(self, iri: str) -> list[SemanticBindingView]: ...
