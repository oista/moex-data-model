"""Asserted ontology relation (edge) in the search projection."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OntologyRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    subject: str
    predicate: str
    object: str
    asserted: bool = True
    source_ontology: str
