"""ModelingStandard envelope."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from moex_modeling.shared.enums import StandardFamily
from moex_modeling.shared.types import AnnotationPair


class ModelingStandard(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    name: str
    description: str | None = None
    annotations: tuple[AnnotationPair, ...] = ()
    version: str
    revision: str
    content_digest: str
    standard_family: StandardFamily
    specification_uri: str
    metamodel_uri: str | None = None
    default_dialect_uri: str | None = None
    semantic_regime: str = "closed_world"
    capabilities: tuple[str, ...] = ()
    media_types: tuple[str, ...] = ()
    canonical_extensions: tuple[str, ...] = ()
