"""ReferenceSpecification envelope."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moex_modeling.shared.enums import SpecificationKind
from moex_modeling.shared.types import AnnotationPair, StandardRef


class ReferenceSpecification(BaseModel):
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
    specification_kind: SpecificationKind
    expressed_in: StandardRef
    root_type: str
    normative_sources: tuple[str, ...] = ()
    imported_specifications: tuple[str, ...] = ()
    conformance_policy: str = "profile"
