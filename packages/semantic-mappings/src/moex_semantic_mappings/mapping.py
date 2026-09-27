"""Semantic binding and resource reference models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

ResourceKind = Literal[
    "ontology_entity",
    "dams_element",
    "glossary_term",
    "linkml_class",
    "linkml_slot",
    "linkml_enum_value",
]


class SemanticResourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    id: str
    kind: ResourceKind
    label: str | None = None


class SemanticBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    subject: SemanticResourceRef
    predicate: str
    object: SemanticResourceRef
    justification: str
    confidence: float | None = None
    author: str | None = None
    status: Literal["proposed", "approved", "rejected"] = "proposed"
    mapping_set_id: str
