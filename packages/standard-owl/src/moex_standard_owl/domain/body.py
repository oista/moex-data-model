"""OWL specification and implementation bodies (distinct types)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class OWLSpecificationBody(BaseModel):
    """Normative release / profile coordinates (not RDF axioms)."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    descriptor_path: str
    ontology_id: str
    ontology_iri: str | None = None
    version_iri: str | None = None
    title: str | None = None
    version: str | None = None
    revision: str | None = None
    content_digest: str | None = None
    role: str | None = None
    status: str | None = None
    imports: tuple[str, ...] = ()
    local_source_hint: str | None = None

    @property
    def path(self) -> Path:
        return Path(self.descriptor_path)


class OWLImplementationBody(BaseModel):
    """Loaded RDF implementation (directory or file set)."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    source_path: str
    ontology_iri: str | None = None
    entity_count: int = 0
    parse_errors: tuple[str, ...] = ()
    _adapter: Any = PrivateAttr(default=None)

    def bind_adapter(self, adapter: Any) -> None:
        object.__setattr__(self, "_adapter", adapter)

    @property
    def adapter(self) -> Any:
        if self._adapter is None:
            raise RuntimeError("adapter not bound; load via OWLStandardProvider")
        return self._adapter

    @property
    def path(self) -> Path:
        return Path(self.source_path)
