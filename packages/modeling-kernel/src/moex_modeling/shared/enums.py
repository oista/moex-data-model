"""Kernel enums aligned with modeling-kernel.yaml."""

from __future__ import annotations

from enum import Enum


class StandardFamily(str, Enum):
    LINKML = "linkml"
    OPENAPI = "openapi"
    OWL = "owl"
    JSON_SCHEMA = "json_schema"
    SHACL = "shacl"
    CUSTOM = "custom"


class SpecificationKind(str, Enum):
    DATA_MODEL = "data_model"
    API_PROFILE = "api_profile"
    ONTOLOGY = "ontology"
    DATA_CONTRACT = "data_contract"
    QUALITY_MODEL = "quality_model"
    VALIDATION_PROFILE = "validation_profile"


class LifecycleStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


class ConformancePhase(str, Enum):
    SOURCE = "source"
    STANDARD_SYNTAX = "standard_syntax"
    STANDARD_SEMANTICS = "standard_semantics"
    SPECIFICATION = "specification"
    CORPORATE_SEMANTICS = "corporate_semantics"
    EXTERNAL_REFERENCES = "external_references"
    COMPATIBILITY = "compatibility"
    ARTIFACT_SMOKE_TEST = "artifact_smoke_test"


class ConformanceResult(str, Enum):
    CONFORMANT = "conformant"
    CONFORMANT_WITH_WARNINGS = "conformant_with_warnings"
    NON_CONFORMANT = "non_conformant"
    INDETERMINATE = "indeterminate"


class TransformationKind(str, Enum):
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    PARTIAL = "partial"
    DERIVED = "derived"


class RelationKind(str, Enum):
    EXPRESSED_IN = "expressed_in"
    CONFORMS_TO = "conforms_to"
    IMPORTS = "imports"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"
    MAPS_TO = "maps_to"
    PROJECTS_TO = "projects_to"
    GENERATED_FROM = "generated_from"


class ImplementationProfile(str, Enum):
    """Discriminator for SpecificationImplementation specialization.

    Orthogonal to ``implementation_kind`` (StandardFamily) and to ADR-016
    publication ``profile`` / ``implements.profile_ref``.
    """

    DAMS_DATA_MODEL = "dams-data-model"
    ONTOLOGY_APPLICATION = "ontology-application"
    API_SPECIFICATION = "api-specification"
    DATA_CONTRACT = "data-contract"
    OTHER = "other"


class DAMSModelLevel(str, Enum):
    """Package-level DAMS model layer — only when profile is dams-data-model.

    Distinct from element-level ModelLevelEnum (conceptual/logical/physical).
    """

    ENTERPRISE_CONCEPTUAL = "enterprise-conceptual"
    SOLUTION = "solution"
