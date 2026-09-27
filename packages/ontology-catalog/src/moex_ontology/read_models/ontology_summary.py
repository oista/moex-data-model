"""Ontology catalog summary for publication."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OntologySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    id: str
    title: str
    version: str
    ontology_iri: str
    version_iri: str | None = None
    status: str
    role: str
    source_uri: str
    imports: tuple[str, ...] = ()
    entity_count: int = 0
    class_count: int = 0
    property_count: int = 0
