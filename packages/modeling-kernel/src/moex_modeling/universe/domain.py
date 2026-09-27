"""ModelUniverse registry graph."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moex_modeling.conformance.domain import ConformanceAssessment, ConformanceReport
from moex_modeling.implementations.domain import SpecificationImplementation
from moex_modeling.shared.enums import RelationKind
from moex_modeling.shared.types import ProvenanceRecord
from moex_modeling.specifications.domain import ReferenceSpecification
from moex_modeling.standards.domain import ModelingStandard


class TypedRelation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    relation_kind: RelationKind
    relation_source: str
    relation_target: str
    relation_provenance: ProvenanceRecord | None = None


class ModelUniverse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    standards: tuple[ModelingStandard, ...] = ()
    specifications: tuple[ReferenceSpecification, ...] = ()
    implementations: tuple[SpecificationImplementation, ...] = ()
    assessments: tuple[ConformanceAssessment, ...] = ()
    reports: tuple[ConformanceReport, ...] = ()
    relations: tuple[TypedRelation, ...] = ()
