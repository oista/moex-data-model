"""LinkML element identities enumerated from schema or instance bodies."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class LinkMLElementKind(str, Enum):
    SCHEMA = "schema"
    CLASS = "class"
    SLOT = "slot"
    TYPE = "type"
    ENUM = "enum"
    INSTANCE = "instance"


class LinkMLElement(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    element_id: str
    kind: LinkMLElementKind
    name: str
    description: str | None = None
