"""LinkML StandardProvider: distinct TSpecBody / TImplBody."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from moex_modeling import (
    Diagnostic,
    DiagnosticSeverity,
    ImplementationRef,
    SpecificationRef,
    StandardFamily,
    StandardProvider,
)

from moex_standard_linkml.adapters.schema_view import load_schema_view, tree_root_class
from moex_standard_linkml.adapters.validator import validate_instance
from moex_standard_linkml.domain.body import (
    LinkMLImplementationBody,
    LinkMLSpecificationBody,
)
from moex_standard_linkml.domain.elements import LinkMLElement, LinkMLElementKind


class LinkMLStandardProvider:
    """
    Concrete StandardProvider for LinkML.

    - specification body: SchemaView summary (schema)
    - implementation body: YAML instance (e.g. ModelPackage)
    """

    family: StandardFamily = StandardFamily.LINKML

    def __init__(
        self,
        *,
        default_schema_path: Path | str | None = None,
        default_target_class: str = "ModelPackage",
    ) -> None:
        self._default_schema_path = (
            Path(default_schema_path) if default_schema_path else None
        )
        self._default_target_class = default_target_class
        self._last_spec: LinkMLSpecificationBody | None = None

    def load_specification_body(
        self,
        specification: SpecificationRef,
        *,
        path: str,
    ) -> LinkMLSpecificationBody:
        schema_path = Path(path)
        sv = load_schema_view(schema_path)
        schema = sv.schema
        body = LinkMLSpecificationBody(
            schema_path=str(schema_path.resolve()),
            schema_id=getattr(schema, "id", None),
            schema_name=getattr(schema, "name", None),
            root_class=tree_root_class(sv),
            class_names=tuple(sorted(sv.all_classes().keys())),
            slot_names=tuple(sorted(sv.all_slots().keys())),
            enum_names=tuple(sorted(sv.all_enums().keys())),
        )
        body.bind_schema_view(sv)
        self._last_spec = body
        self._default_schema_path = schema_path
        _ = specification  # coordinate reserved for future registry lookup
        return body

    def load_implementation_body(
        self,
        implementation: ImplementationRef,
        *,
        path: str,
    ) -> LinkMLImplementationBody:
        source = Path(path)
        data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError(f"implementation YAML must be a mapping: {source}")
        _ = implementation
        return LinkMLImplementationBody(
            source_path=str(source.resolve()),
            target_class=self._default_target_class,
            data=data,
        )

    def enumerate_elements(
        self,
        body: LinkMLImplementationBody,
    ) -> tuple[LinkMLElement, ...]:
        """Enumerate top-level instance collections as LinkML elements."""
        elements: list[LinkMLElement] = []
        root_id = body.element_id or body.name or "instance"
        elements.append(
            LinkMLElement(
                element_id=str(root_id),
                kind=LinkMLElementKind.INSTANCE,
                name=str(body.name or root_id),
                description=body.data.get("description"),
            )
        )
        for collection in (
            "conceptual_entities",
            "logical_entities",
            "data_carriers",
            "access_points",
            "data_containers",
            "execution_assets",
            "domain_contexts",
            "mappings",
        ):
            items = body.data.get(collection) or []
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                eid = item.get("element_id") or item.get("name")
                if not eid:
                    continue
                elements.append(
                    LinkMLElement(
                        element_id=str(eid),
                        kind=LinkMLElementKind.INSTANCE,
                        name=str(item.get("name") or eid),
                        description=item.get("description"),
                    )
                )
        return tuple(elements)

    def validate_standard(
        self,
        body: LinkMLImplementationBody,
    ) -> tuple[Diagnostic, ...]:
        schema_path = self._default_schema_path
        if schema_path is None and self._last_spec is not None:
            schema_path = self._last_spec.path
        if schema_path is None:
            return (
                Diagnostic(
                    diagnostic_code="LINKML-NO-SCHEMA",
                    severity=DiagnosticSeverity.FATAL,
                    diagnostic_message=(
                        "No schema path: call load_specification_body first "
                        "or pass default_schema_path to the provider"
                    ),
                ),
            )
        return validate_instance(body, schema_path)


def as_standard_provider(provider: LinkMLStandardProvider) -> StandardProvider[
    LinkMLSpecificationBody,
    LinkMLImplementationBody,
    LinkMLElement,
]:
    """Type helper asserting protocol conformance."""
    return provider
