"""SSSOM mapping set envelope."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moex_semantic_mappings.mapping import SemanticBinding


class MappingSet(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    mapping_set_id: str
    mapping_set_version: str
    license: str | None = None
    mappings: tuple[SemanticBinding, ...] = ()
