"""SpecificationImplementation envelope (typed body lives in providers)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moex_modeling.shared.enums import (
    DAMSModelLevel,
    ImplementationProfile,
    LifecycleStatus,
    StandardFamily,
)
from moex_modeling.shared.types import (
    AnnotationPair,
    ProvenanceRecord,
    SourceDescriptor,
    SpecificationRef,
)


class SpecificationImplementation(BaseModel):
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
    conforms_to: SpecificationRef
    implementation_kind: StandardFamily
    lifecycle_status: LifecycleStatus = LifecycleStatus.DRAFT
    source: SourceDescriptor
    provenance: ProvenanceRecord | None = None
    body_ref: str | None = None
    # Orthogonal to implementation_kind (StandardFamily) and ADR-016 publish profile.
    implementation_profile: ImplementationProfile | None = None
    # Only valid when implementation_profile == dams-data-model (ADR-021).
    dams_model_level: DAMSModelLevel | None = None
