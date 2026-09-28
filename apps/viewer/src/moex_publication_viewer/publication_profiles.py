"""Publication profiles: mandatory PublicationSectionRole per ModelingStandardFamily."""

from __future__ import annotations

from typing import Literal

ModelingStandardFamily = Literal[
    "linkml",
    "openapi",
    "owl",
    "json_schema",
    "shacl",
    "custom",
]

PublicationSectionRole = Literal[
    "overview",
    "classes",
    "specification",
    "glossary",
    "requirements",
    "implementations",
]

# Canonical profiles (DSP PublicationProfile). Optional roles may appear beyond these.
REQUIRED_ROLES: dict[str, frozenset[str]] = {
    "linkml": frozenset({"overview", "classes", "specification", "glossary"}),
    "owl": frozenset({"overview", "classes", "glossary"}),
}

# Explorer group section_root → PublicationSectionRole
SECTION_ROOT_TO_ROLE: dict[str, str] = {
    "overview": "overview",
    "classes": "classes",
    "spec-files": "specification",
    "specification": "specification",
    "glossary": "glossary",
    "requirements": "requirements",
    "implementations": "implementations",
}


def required_roles_for(standard: str | None) -> frozenset[str] | None:
    if not standard:
        return None
    return REQUIRED_ROLES.get(standard)
