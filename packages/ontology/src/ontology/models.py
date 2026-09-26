"""Dataclasses for ontology entity occurrences and export rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParseError:
    """Record of a failed RDF file parse."""

    module_path: str
    exception_type: str
    exception_message: str


@dataclass(slots=True)
class EntityOccurrence:
    """One entity declaration found in a single RDF module file."""

    iri: str
    local_name: str
    label: str | None
    definition: str | None
    entity_type: str  # owl:Class, owl:ObjectProperty, ...
    entity_type_code: str  # class, object_property, ...
    module_iri: str | None
    module_path: str
    is_deprecated: bool
    deprecated_replacement_iri: str | None
    superclasses: str | None
    source_release: str
    source_file_sha256: str
    # Technical / optional fields
    alternative_labels: str | None = None
    definition_language: str | None = None
    label_language: str | None = None
    ontology_version_iri: str | None = None
    imports: str | None = None
    source_domain: str | None = None
    parse_status: str = "ok"
    parse_error: str | None = None


@dataclass(slots=True)
class AggregatedEntity:
    """Entity aggregated across modules by iri + entity_type."""

    iri: str
    local_name: str
    label: str | None
    definition: str | None
    entity_type: str
    entity_type_code: str
    module_iri: str | None
    module_path: str
    is_deprecated: bool
    deprecated_replacement_iri: str | None
    superclasses: str | None
    source_release: str
    source_file_sha256: str
    alternative_labels: str | None = None
    definition_language: str | None = None
    label_language: str | None = None
    ontology_version_iri: str | None = None
    imports: str | None = None
    source_domain: str | None = None
    parse_status: str = "ok"
    parse_error: str | None = None

    def to_core_dict(self) -> dict[str, Any]:
        """Core mart columns for CSV / primary Excel sheets."""
        return {
            "iri": self.iri,
            "local_name": self.local_name,
            "label": self.label,
            "definition": self.definition,
            "entity_type": self.entity_type,
            "module_iri": self.module_iri,
            "module_path": self.module_path,
            "is_deprecated": self.is_deprecated,
            "deprecated_replacement_iri": self.deprecated_replacement_iri,
            "superclasses": self.superclasses,
            "source_release": self.source_release,
            "source_file_sha256": self.source_file_sha256,
        }

    def to_technical_dict(self) -> dict[str, Any]:
        """Core columns plus technical details."""
        row = self.to_core_dict()
        row.update(
            {
                "entity_type_code": self.entity_type_code,
                "alternative_labels": self.alternative_labels,
                "definition_language": self.definition_language,
                "label_language": self.label_language,
                "ontology_version_iri": self.ontology_version_iri,
                "imports": self.imports,
                "source_domain": self.source_domain,
                "parse_status": self.parse_status,
                "parse_error": self.parse_error,
            }
        )
        return row


@dataclass(slots=True)
class ExportManifest:
    """JSON manifest describing an export run."""

    generated_at_utc: str
    source_path: str
    source_release: str
    included_domains: list[str]
    included_types: list[str]
    include_examples: bool
    include_individuals: bool
    include_deprecated: bool
    processed_files: int
    successful_files: int
    failed_files: int
    entities_total: int
    entities_active: int
    entities_deprecated: int
    entities_without_definition: int
    output_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at_utc": self.generated_at_utc,
            "source_path": self.source_path,
            "source_release": self.source_release,
            "included_domains": self.included_domains,
            "included_types": self.included_types,
            "include_examples": self.include_examples,
            "include_individuals": self.include_individuals,
            "include_deprecated": self.include_deprecated,
            "processed_files": self.processed_files,
            "successful_files": self.successful_files,
            "failed_files": self.failed_files,
            "entities_total": self.entities_total,
            "entities_active": self.entities_active,
            "entities_deprecated": self.entities_deprecated,
            "entities_without_definition": self.entities_without_definition,
            "output_files": self.output_files,
        }


CORE_COLUMNS: tuple[str, ...] = (
    "iri",
    "local_name",
    "label",
    "definition",
    "entity_type",
    "module_iri",
    "module_path",
    "is_deprecated",
    "deprecated_replacement_iri",
    "superclasses",
    "source_release",
    "source_file_sha256",
)

TECHNICAL_COLUMNS: tuple[str, ...] = CORE_COLUMNS + (
    "entity_type_code",
    "alternative_labels",
    "definition_language",
    "label_language",
    "ontology_version_iri",
    "imports",
    "source_domain",
    "parse_status",
    "parse_error",
)

PARSE_ERROR_COLUMNS: tuple[str, ...] = (
    "module_path",
    "exception_type",
    "exception_message",
)
