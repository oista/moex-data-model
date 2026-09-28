"""Stable public API for moex-modeling-kernel."""

from moex_modeling.assets.public import SchemaRepository
from moex_modeling.identifiers.curie import CurieUriResolver
from moex_modeling.changes.domain import (
    ChangeCategory,
    SemanticChange,
    SemanticDiffReport,
)
from moex_modeling.conformance.domain import (
    ConformanceAssessment,
    ConformanceReport,
    Diagnostic,
    summarize_result,
)
from moex_modeling.conformance.wire import diagnostic_to_wire
from moex_modeling.implementations.domain import SpecificationImplementation
from moex_modeling.shared.enums import (
    ConformancePhase,
    ConformanceResult,
    DiagnosticSeverity,
    LifecycleStatus,
    RelationKind,
    SpecificationKind,
    StandardFamily,
    TransformationKind,
)
from moex_modeling.shared.types import (
    AnnotationPair,
    DiagnosticDetail,
    ImplementationRef,
    ProvenanceRecord,
    SourceDescriptor,
    SourceLocation,
    SpecificationRef,
    StandardRef,
)
from moex_modeling.specifications.domain import ReferenceSpecification
from moex_modeling.standards.domain import ModelingStandard
from moex_modeling.standards.public import (
    LoadedImplementation,
    StandardProvider,
    TElement,
    TImplBody,
    TSpecBody,
)
from moex_modeling.universe.domain import ModelUniverse, TypedRelation

__all__ = [
    "AnnotationPair",
    "ChangeCategory",
    "ConformanceAssessment",
    "ConformancePhase",
    "ConformanceReport",
    "ConformanceResult",
    "CurieUriResolver",
    "Diagnostic",
    "DiagnosticDetail",
    "DiagnosticSeverity",
    "ImplementationRef",
    "LifecycleStatus",
    "LoadedImplementation",
    "ModelUniverse",
    "ModelingStandard",
    "ProvenanceRecord",
    "ReferenceSpecification",
    "RelationKind",
    "SchemaRepository",
    "SemanticChange",
    "SemanticDiffReport",
    "SourceDescriptor",
    "SourceLocation",
    "SpecificationImplementation",
    "SpecificationKind",
    "SpecificationRef",
    "StandardFamily",
    "StandardProvider",
    "StandardRef",
    "TElement",
    "TImplBody",
    "TSpecBody",
    "TransformationKind",
    "TypedRelation",
    "diagnostic_to_wire",
    "summarize_result",
]
