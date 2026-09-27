"""Ontology release descriptor / indexed release."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

OntologyReleaseStatus = Literal["registered", "indexed", "invalid", "deprecated"]


class OntologyRelease(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    id: str
    ontology_iri: str
    version_iri: str | None = None
    title: str
    version: str
    source_uri: str
    revision: str
    content_digest: str
    license_uri: str | None = None
    imports: tuple[str, ...] = ()
    status: OntologyReleaseStatus = "registered"
    role: Literal["reference", "implementation"] = "reference"
    local_source_hint: str | None = Field(
        default=None,
        description="Optional relative path hint for local RDF checkout (not fetched).",
    )

    @field_validator("imports", mode="before")
    @classmethod
    def coerce_imports(cls, value: object) -> object:
        if isinstance(value, list):
            return tuple(value)
        return value
