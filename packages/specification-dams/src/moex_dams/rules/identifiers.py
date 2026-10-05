"""CURIE/URI well-formedness rules for DAMS ModelPackage identifiers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from linkml_runtime import SchemaView
from moex_modeling import (
    ConformancePhase,
    CurieUriResolver,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
    SourceLocation,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.mappings.dams_to_graph import package_index


def _prefix_reference(value: Any) -> str:
    if hasattr(value, "prefix_reference"):
        return str(value.prefix_reference)
    return str(value)


def load_schema_prefix_map(schema_path: Path | str) -> tuple[dict[str, str], str | None]:
    """Load prefixes + default_prefix from a LinkML schema YAML (top-level only)."""
    path = Path(schema_path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    prefixes = dict(data.get("prefixes") or {})
    # Resolve CURIE-style prefix values that point at another prefix key.
    resolved: dict[str, str] = {}
    for key, value in prefixes.items():
        text = str(value)
        if text.startswith("http://") or text.startswith("https://"):
            resolved[str(key)] = text
        elif ":" in text:
            pref, _, local = text.partition(":")
            base = prefixes.get(pref)
            if isinstance(base, str) and (
                base.startswith("http://") or base.startswith("https://")
            ):
                resolved[str(key)] = base + local
            else:
                resolved[str(key)] = text
        else:
            resolved[str(key)] = text
    default = data.get("default_prefix")
    return resolved, str(default) if default else None


def load_schema_view(
    schema_path: Path | str, *, merge_imports: bool = False
) -> SchemaView:
    """Load SchemaView and force import closure so ``schema_map`` is populated."""
    sv = SchemaView(str(schema_path), merge_imports=merge_imports)
    sv.imports_closure()
    return sv


def load_merged_schema_prefix_map(
    schema_path: Path | str,
) -> tuple[dict[str, str], str | None]:
    """
    Merge prefixes from the root schema and all SchemaView imports.

    On conflicting URI for the same key, keeps the first-seen value; callers
    should run ``check_ontology_uris`` for ``MOEX-ONT-003``.
    """
    sv = load_schema_view(schema_path, merge_imports=False)
    merged: dict[str, str] = {}
    for schema in sv.schema_map.values():
        for key, value in (schema.prefixes or {}).items():
            text = _prefix_reference(value)
            if not text:
                continue
            merged.setdefault(str(key), text)
    default = sv.schema.default_prefix
    return merged, str(default) if default else None


def build_dams_curie_resolver(schema_path: Path | str) -> CurieUriResolver:
    prefixes, default_prefix = load_merged_schema_prefix_map(schema_path)
    return CurieUriResolver.from_schema_prefixes(
        prefixes, default_prefix=default_prefix
    )


def _pointer(collection: str, element_id: str) -> str:
    return f"/{collection}/{element_id}"


def _walk_ids(data: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return (value, subject_element_id, collection) for ids and refs."""
    found: list[tuple[str, str, str]] = []
    index = package_index(data)
    for eid in index:
        found.append((eid, eid, "elements"))

    for entity in data.get("logical_entities") or []:
        if not isinstance(entity, dict):
            continue
        eid = str(entity.get("element_id") or "")
        for cref in entity.get("conceptual_entity_refs") or []:
            found.append((str(cref), eid, "logical_entities"))
        ctx = entity.get("context_ref")
        if ctx:
            found.append((str(ctx), eid, "logical_entities"))

    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        rid = str(rel.get("element_id") or "")
        for key in ("source_entity_ref", "target_entity_ref"):
            ref = rel.get(key)
            if ref:
                found.append((str(ref), rid, "relationships"))

    for mapping in data.get("mappings") or []:
        if not isinstance(mapping, dict):
            continue
        mid = str(mapping.get("element_id") or "")
        for ref in list(mapping.get("source_refs") or []) + list(
            mapping.get("target_refs") or []
        ):
            found.append((str(ref), mid, "mappings"))

    return found


def check_identifiers(
    body: LinkMLImplementationBody,
    *,
    resolver: CurieUriResolver,
) -> tuple[Diagnostic, ...]:
    """Emit MOEX-ID-001 for CURIEs whose prefix is not in the schema map."""
    diagnostics: list[Diagnostic] = []
    source_uri = body.source_path or None
    seen: set[str] = set()

    for value, subject, collection in _walk_ids(body.data):
        if not value or value in seen:
            continue
        seen.add(value)
        unknown = resolver.unknown_prefix(value)
        if unknown is None:
            continue
        diagnostics.append(
            Diagnostic(
                diagnostic_code="MOEX-ID-001",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message=(
                    f"Unknown CURIE prefix {unknown!r} in identifier {value!r}"
                ),
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=subject or None,
                source_location=SourceLocation(
                    source_uri=source_uri,
                    json_pointer=_pointer(collection, subject or value),
                )
                if subject or source_uri
                else None,
                diagnostic_details=(
                    DiagnosticDetail(
                        detail_key="suggestion",
                        detail_value=(
                            f"Declare prefix {unknown!r} in the DAMS schema "
                            "or use a known prefix (e.g. dams:)"
                        ),
                    ),
                    DiagnosticDetail(detail_key="prefix", detail_value=unknown),
                ),
            )
        )

    return tuple(diagnostics)


__all__ = [
    "build_dams_curie_resolver",
    "check_identifiers",
    "load_merged_schema_prefix_map",
    "load_schema_prefix_map",
    "load_schema_view",
]
