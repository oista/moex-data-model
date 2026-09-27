"""Cross-resource identity for semantic bindings."""

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
