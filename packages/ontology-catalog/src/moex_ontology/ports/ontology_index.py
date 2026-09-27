"""Port: rebuildable ontology search index."""

from __future__ import annotations

from typing import Protocol

from moex_ontology.domain.entity import OntologyEntity
from moex_ontology.domain.ontology import OntologyRelease
from moex_ontology.domain.relation import OntologyRelation


class OntologyIndexPort(Protocol):
    def replace_all(
        self,
        *,
        releases: list[OntologyRelease],
        entities: list[OntologyEntity],
        relations: list[OntologyRelation],
    ) -> None: ...

    def list_releases(self) -> list[OntologyRelease]: ...

    def get_release(self, ontology_id: str) -> OntologyRelease | None: ...

    def get_entity(self, iri: str) -> OntologyEntity | None: ...

    def search_entities(self, query: str, *, limit: int = 50) -> list[OntologyEntity]: ...

    def relations_for(
        self,
        iri: str,
        *,
        predicate: str | None = None,
    ) -> list[OntologyRelation]: ...

    def entity_count(self, ontology_id: str) -> int: ...

    def list_entities(self, *, ontology_id: str | None = None) -> list[OntologyEntity]: ...
