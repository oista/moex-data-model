"""OWL element identities enumerated from an implementation body."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class OWLElementKind(str, Enum):
    ONTOLOGY = "ontology"
    CLASS = "class"
    OBJECT_PROPERTY = "object_property"
    DATA_PROPERTY = "data_property"
    ANNOTATION_PROPERTY = "annotation_property"
    INDIVIDUAL = "individual"
    UNKNOWN = "unknown"


class OWLElement(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    element_id: str
    kind: OWLElementKind
    name: str
    description: str | None = None
