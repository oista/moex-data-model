"""Ontology entity read model over an OWL resource."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

OntologyEntityKind = Literal[
    "class",
    "object_property",
    "data_property",
    "annotation_property",
    "individual",
]


class OntologyEntity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    iri: str
    ontology_id: str
    kind: OntologyEntityKind
    label: str | None = None
    definition: str | None = None
    alternative_labels: tuple[str, ...] = ()
    deprecated: bool = False
    replaced_by: str | None = None
