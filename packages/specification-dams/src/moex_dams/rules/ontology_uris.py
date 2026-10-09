"""Schema-level URI / prefix lint for DAMS LinkML (ADR-030)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from linkml_runtime import SchemaView
from moex_modeling import (
    ConformancePhase,
    CurieUriResolver,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
    SourceLocation,
)

from moex_dams.rules.identifiers import (
    _prefix_reference,
    load_merged_schema_prefix_map,
    load_schema_view,
)


def _diag(
    code: str,
    message: str,
    *,
    subject: str | None = None,
    pointer: str | None = None,
    source_uri: str | None = None,
    details: tuple[DiagnosticDetail, ...] = (),
) -> Diagnostic:
    return Diagnostic(
        diagnostic_code=code,
        severity=DiagnosticSeverity.ERROR,
        diagnostic_message=message,
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        source_location=SourceLocation(
            source_uri=source_uri,
            json_pointer=pointer,
        )
        if source_uri or pointer
        else None,
        diagnostic_details=details,
    )


def _expand_element_iri(
    sv: SchemaView,
    resolver: CurieUriResolver,
    element: Any,
) -> str | None:
    """Return expanded IRI for a class/slot/enum via SchemaView, with fallback."""
    try:
        uri = sv.get_uri(element, expand=True)
    except Exception:  # noqa: BLE001 — SchemaView may raise on incomplete defs
        uri = None
    if uri:
        return str(uri)
    name = getattr(element, "name", None)
    if not name:
        return None
    return resolver.expand(str(name))


def check_ontology_uris(schema_path: Path | str) -> tuple[Diagnostic, ...]:
    """
    Lint DAMS schema IRIs and prefixes (MOEX-ONT-001…004).

    Does not assess ModelPackage instances.
    """
    path = Path(schema_path)
    source_uri = path.as_posix()
    # merge_imports=False so prefix conflicts are still visible on each schema
    prefix_sv = load_schema_view(path, merge_imports=False)
    # merged view for element URI expansion across imports
    sv = load_schema_view(path, merge_imports=True)
    prefixes, default_prefix = load_merged_schema_prefix_map(path)
    resolver = CurieUriResolver.from_schema_prefixes(
        prefixes, default_prefix=default_prefix
    )
    diagnostics: list[Diagnostic] = []

    # MOEX-ONT-003 / MOEX-ONT-004 — walk every import's declared prefixes
    seen_prefix: dict[str, str] = {}
    for schema_name, schema in prefix_sv.schema_map.items():
        for key, value in (schema.prefixes or {}).items():
            text = _prefix_reference(value)
            if not text:
                continue
            if not (text.endswith("/") or text.endswith("#")):
                # INV-026 (ADR-030): prefix URI must end with '/' or '#'
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-004",
                        (
                            f"Prefix {key!r} in schema {schema_name!r} has URI "
                            f"{text!r} without trailing '/' or '#' (INV-026)."
                        ),
                        subject=str(key),
                        pointer=f"/prefixes/{key}",
                        source_uri=source_uri,
                        details=(
                            DiagnosticDetail(
                                detail_key="schema", detail_value=str(schema_name)
                            ),
                            DiagnosticDetail(detail_key="uri", detail_value=text),
                            DiagnosticDetail(
                                detail_key="invariant_id", detail_value="INV-026"
                            ),
                            DiagnosticDetail(
                                detail_key="remediation",
                                detail_value=(
                                    "Append '/' or '#' to the prefix URI. INV-026."
                                ),
                            ),
                        ),
                    )
                )
            prior = seen_prefix.get(str(key))
            if prior is not None and prior != text:
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-003",
                        (
                            f"Prefix {key!r} maps to conflicting URIs: "
                            f"{prior!r} vs {text!r} (schema {schema_name!r})"
                        ),
                        subject=str(key),
                        pointer=f"/prefixes/{key}",
                        source_uri=source_uri,
                        details=(
                            DiagnosticDetail(
                                detail_key="schema", detail_value=str(schema_name)
                            ),
                            DiagnosticDetail(
                                detail_key="uri_a", detail_value=prior
                            ),
                            DiagnosticDetail(
                                detail_key="uri_b", detail_value=text
                            ),
                        ),
                    )
                )
            else:
                seen_prefix.setdefault(str(key), text)

    # MOEX-ONT-002 — explicit class_uri / slot_uri / meaning must expand
    for class_name, cls in sv.all_classes().items():
        for attr in ("class_uri", "meaning"):
            raw = getattr(cls, attr, None)
            if not raw:
                continue
            if resolver.expand(str(raw)) is None:
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-002",
                        (
                            f"Class {class_name!r} {attr}={raw!r} does not "
                            "expand to an absolute URI"
                        ),
                        subject=class_name,
                        pointer=f"/classes/{class_name}/{attr}",
                        source_uri=source_uri,
                    )
                )
    for slot_name, slot in sv.all_slots().items():
        for attr in ("slot_uri", "meaning"):
            raw = getattr(slot, attr, None)
            if not raw:
                continue
            if resolver.expand(str(raw)) is None:
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-002",
                        (
                            f"Slot {slot_name!r} {attr}={raw!r} does not "
                            "expand to an absolute URI"
                        ),
                        subject=slot_name,
                        pointer=f"/slots/{slot_name}/{attr}",
                        source_uri=source_uri,
                    )
                )

    # MOEX-ONT-001 — IRI collisions across classes / slots / enums / values
    owners: dict[str, str] = {}
    for class_name, cls in sv.all_classes().items():
        iri = _expand_element_iri(sv, resolver, cls)
        if not iri:
            continue
        label = f"class:{class_name}"
        if iri in owners and owners[iri] != label:
            diagnostics.append(
                _diag(
                    "MOEX-ONT-001",
                    f"IRI collision: {iri!r} owned by {owners[iri]} and {label}",
                    subject=class_name,
                    pointer=f"/classes/{class_name}",
                    source_uri=source_uri,
                )
            )
        else:
            owners[iri] = label

    for slot_name, slot in sv.all_slots().items():
        iri = _expand_element_iri(sv, resolver, slot)
        if not iri:
            continue
        label = f"slot:{slot_name}"
        if iri in owners and owners[iri] != label:
            diagnostics.append(
                _diag(
                    "MOEX-ONT-001",
                    f"IRI collision: {iri!r} owned by {owners[iri]} and {label}",
                    subject=slot_name,
                    pointer=f"/slots/{slot_name}",
                    source_uri=source_uri,
                )
            )
        else:
            owners[iri] = label

    for enum_name, enum in sv.all_enums().items():
        enum_iri = _expand_element_iri(sv, resolver, enum)
        if enum_iri:
            label = f"enum:{enum_name}"
            if enum_iri in owners and owners[enum_iri] != label:
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-001",
                        (
                            f"IRI collision: {enum_iri!r} owned by "
                            f"{owners[enum_iri]} and {label}"
                        ),
                        subject=enum_name,
                        pointer=f"/enums/{enum_name}",
                        source_uri=source_uri,
                    )
                )
            else:
                owners[enum_iri] = label
            base = enum_iri
        else:
            base = resolver.expand(enum_name) or ""
        for pv_name in (enum.permissible_values or {}):
            value_iri = f"{base}#{pv_name}" if base else None
            if not value_iri:
                continue
            label = f"enum_value:{enum_name}#{pv_name}"
            if value_iri in owners and owners[value_iri] != label:
                diagnostics.append(
                    _diag(
                        "MOEX-ONT-001",
                        (
                            f"IRI collision: {value_iri!r} owned by "
                            f"{owners[value_iri]} and {label}"
                        ),
                        subject=f"{enum_name}#{pv_name}",
                        pointer=f"/enums/{enum_name}/permissible_values/{pv_name}",
                        source_uri=source_uri,
                    )
                )
            else:
                owners[value_iri] = label

    return tuple(diagnostics)


__all__ = ["check_ontology_uris"]
