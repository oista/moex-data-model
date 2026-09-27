"""Semantic binding views for cards and backlinks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class SemanticBindingView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    subject_id: str
    subject_label: str | None = None
    subject_kind: str
    predicate: str
    object_id: str
    object_label: str | None = None
    object_kind: str
    justification: str
    confidence: float | None = None
    author: str | None = None
    status: Literal["proposed", "approved", "rejected"] = "proposed"
    mapping_set_id: str


class SemanticContext(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    entity_iri: str
    bindings: tuple[SemanticBindingView, ...] = ()
