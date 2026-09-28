"""DAMS-backed SchemaRepository over LinkMLStandardProvider."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import ImplementationRef, SpecificationRef
from moex_standard_linkml.domain.body import (
    LinkMLImplementationBody,
    LinkMLSpecificationBody,
)
from moex_standard_linkml.provider import LinkMLStandardProvider

DAMS_SPEC_ID = "moex:spec:dams"
DAMS_VERSION = "0.1.0"
LINKML_STANDARD_ID = "moex:standard:linkml"


class DamsAssetRepository:
    """
    Resolve moex:spec:dams assets and load LinkML bodies.

    Composes LinkMLStandardProvider; does not replace it.
    """

    def __init__(
        self,
        *,
        default_schema_path: Path | str | None = None,
        provider: LinkMLStandardProvider | None = None,
        default_target_class: str = "ModelPackage",
    ) -> None:
        schema = Path(default_schema_path) if default_schema_path else None
        self._default_schema_path = schema.resolve() if schema is not None else None
        self._provider = provider or LinkMLStandardProvider(
            default_schema_path=self._default_schema_path,
            default_target_class=default_target_class,
        )

    @property
    def provider(self) -> LinkMLStandardProvider:
        return self._provider

    def resolve_specification_path(self, specification: SpecificationRef) -> Path:
        if specification.specification_id != DAMS_SPEC_ID:
            raise ValueError(
                f"unsupported specification_id: {specification.specification_id!r} "
                f"(expected {DAMS_SPEC_ID!r})"
            )
        version = specification.specification_version or ""
        if version not in {"0.1", "0.1.0", DAMS_VERSION}:
            raise ValueError(
                f"unsupported dams specification_version: {version!r}"
            )
        if self._default_schema_path is None:
            raise ValueError("DamsAssetRepository has no default_schema_path")
        return self._default_schema_path

    def load_specification(
        self, specification: SpecificationRef
    ) -> LinkMLSpecificationBody:
        path = self.resolve_specification_path(specification)
        return self._provider.load_specification_body(specification, path=str(path))

    def load_implementation(
        self,
        implementation: ImplementationRef,
        *,
        path: Path | str,
    ) -> LinkMLImplementationBody:
        return self._provider.load_implementation_body(
            implementation, path=str(Path(path))
        )

    def validate_standard(
        self, body: LinkMLImplementationBody
    ) -> tuple:
        return self._provider.validate_standard(body)
