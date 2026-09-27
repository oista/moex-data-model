"""Entity card and tree node read models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from moex_ontology.read_models.semantic_context import SemanticBindingView


class OntologyTreeNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    id: str
    title: str | None = None
    description: str | None = None
    children: tuple["OntologyTreeNode", ...] = ()
    attributes: dict[str, str | int | bool | None] = Field(default_factory=dict)


class OntologyEntityCard(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    iri: str
    curie: str | None = None
    ontology_id: str
    kind: str
    label: str | None = None
    definition: str | None = None
    aliases: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    children: tuple[str, ...] = ()
    domain: tuple[str, ...] = ()
    range: tuple[str, ...] = ()
    deprecated: bool = False
    replaced_by: str | None = None
    related_model_elements: tuple[SemanticBindingView, ...] = ()
    related_glossary_terms: tuple[SemanticBindingView, ...] = ()
    external_mappings: tuple[SemanticBindingView, ...] = ()
