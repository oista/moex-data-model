"""OWL application ontology provider descriptor (ADR-018)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, field_validator


class OntologyApplicationDescriptor(BaseModel):
    """Sidecar governance for an OWL SpecificationImplementation application ontology.

    Kernel envelope stays generic; these fields are provider-owned (ADR-018).
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    namespace_iri: str
    conformance_level: str
    seed_ref: str
    imported_module_ref: str
    extension_ref: str
    mapping_ref: str
    sssom_ref: str | None = None
    external_source_id: str | None = None
    descriptor_path: str | None = None

    @field_validator(
        "id",
        "namespace_iri",
        "conformance_level",
        "seed_ref",
        "imported_module_ref",
        "extension_ref",
        "mapping_ref",
        mode="before",
    )
    @classmethod
    def _non_empty_str(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @property
    def path(self) -> Path:
        if not self.descriptor_path:
            raise RuntimeError("descriptor_path not set")
        return Path(self.descriptor_path)

    def base_dir(self) -> Path:
        return self.path.parent

    def resolve_ref(self, relative: str) -> Path:
        return (self.base_dir() / relative).resolve()

    def artifact_paths(self) -> dict[str, Path]:
        return {
            "imported_module": self.resolve_ref(self.imported_module_ref),
            "extension": self.resolve_ref(self.extension_ref),
            "mapping": self.resolve_ref(self.mapping_ref),
        }

    def missing_artifacts(self) -> tuple[str, ...]:
        missing: list[str] = []
        for name, path in self.artifact_paths().items():
            if not path.is_file():
                missing.append(f"{name}:{path}")
        return tuple(missing)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping in {path}")
    return data


def load_ontology_application_descriptor(
    path: Path,
    *,
    require_artifacts: bool = True,
) -> OntologyApplicationDescriptor:
    """Load ``ontology-application.yaml`` and optionally assert metamodel TTL files exist."""
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"missing ontology application descriptor: {path}")
    raw = _load_yaml(path)
    descriptor = OntologyApplicationDescriptor.model_validate(
        {**raw, "descriptor_path": str(path)}
    )
    if require_artifacts:
        missing = descriptor.missing_artifacts()
        if missing:
            raise FileNotFoundError(
                "application ontology artifacts missing: " + "; ".join(missing)
            )
    return descriptor
