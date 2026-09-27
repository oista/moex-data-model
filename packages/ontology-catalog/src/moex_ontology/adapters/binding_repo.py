"""Adapt semantic-mappings MappingSet to catalog SemanticBindingRepositoryPort."""

from __future__ import annotations

from moex_ontology.read_models.semantic_context import SemanticBindingView


class MappingSetBindingRepository:
    def __init__(self, mapping_set) -> None:
        self._bindings = list(mapping_set.mappings)

    def list_bindings(
        self,
        *,
        subject_id: str | None = None,
        object_id: str | None = None,
        mapping_set_id: str | None = None,
    ) -> list[SemanticBindingView]:
        result: list[SemanticBindingView] = []
        for b in self._bindings:
            if subject_id and b.subject.id != subject_id:
                continue
            if object_id and b.object.id != object_id:
                continue
            if mapping_set_id and b.mapping_set_id != mapping_set_id:
                continue
            result.append(self._view(b))
        return result

    def backlinks_for_ontology_entity(self, iri: str) -> list[SemanticBindingView]:
        return [
            self._view(b)
            for b in self._bindings
            if b.object.id == iri or b.subject.id == iri
        ]

    @staticmethod
    def _view(b) -> SemanticBindingView:
        return SemanticBindingView(
            subject_id=b.subject.id,
            subject_label=b.subject.label,
            subject_kind=b.subject.kind,
            predicate=b.predicate,
            object_id=b.object.id,
            object_label=b.object.label,
            object_kind=b.object.kind,
            justification=b.justification,
            confidence=b.confidence,
            author=b.author,
            status=b.status,
            mapping_set_id=b.mapping_set_id,
        )
