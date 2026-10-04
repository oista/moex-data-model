"""Publication profiles (ADR-016): ProfileSpec + renderer mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PublicationProfileId = Literal[
    "linkml-specification",
    "ontology",
    "implementation",
]

PublicationSectionKind = Literal[
    "overview",
    "classes",
    "slots",
    "enumerations",
    "schema-files",
    "taxonomy",
    "glossary",
    "identity",
    "bindings",
    "data-flows",
    "conformance",
    "model-assessment",
    "source",
    "external-specification-scope",
    "competency-questions",
    "term-selection",
    "mapping-table",
    "dependency-list",
    "extraction-provenance",
]


@dataclass(frozen=True)
class ProfileSpec:
    required: frozenset[str]
    recommended: frozenset[str]
    forbidden: frozenset[str]


PROFILES: dict[str, ProfileSpec] = {
    "linkml-specification": ProfileSpec(
        required=frozenset({"overview", "classes", "schema-files"}),
        recommended=frozenset({"enumerations", "slots"}),
        forbidden=frozenset({"taxonomy"}),
    ),
    "ontology": ProfileSpec(
        # ADR-024: classes + glossary required; taxonomy deprecated for new modules.
        required=frozenset({"overview", "classes", "glossary"}),
        recommended=frozenset({"schema-files", "identity"}),
        forbidden=frozenset({"enumerations", "slots"}),
    ),
    "implementation": ProfileSpec(
        required=frozenset({"overview", "conformance"}),
        recommended=frozenset({"bindings", "data-flows", "model-assessment"}),
        forbidden=frozenset({"taxonomy"}),
    ),
}

# Explorer group section_root → PublicationSectionKind
SECTION_ROOT_TO_KIND: dict[str, str] = {
    "overview": "overview",
    "classes": "classes",
    "spec-files": "schema-files",
    "schema-files": "schema-files",
    "taxonomy": "taxonomy",
    "glossary": "glossary",
    "identity": "identity",
    "slots": "slots",
    "enumerations": "enumerations",
    "conformance": "conformance",
    "model-assessment": "model-assessment",
    "bindings": "bindings",
    "data-flows": "data-flows",
    "source": "source",
    "external-specification-scope": "external-specification-scope",
    "competency-questions": "competency-questions",
    "term-selection": "term-selection",
    "mapping-table": "mapping-table",
    "dependency-list": "dependency-list",
    "extraction-provenance": "extraction-provenance",
}


def get_renderer_mode(section_kind: str, profile: str | None) -> str:
    """Return renderer mode for a semantic section kind under a profile."""
    if section_kind == "classes":
        if profile == "ontology":
            return "ontology-list"
        return "data-structure"
    return section_kind


def profile_spec(profile: str | None) -> ProfileSpec | None:
    if not profile:
        return None
    return PROFILES.get(profile)
