"""Reference integrity rules for DAMS ModelPackage."""

from __future__ import annotations

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
    SourceLocation,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.mappings.dams_to_graph import package_index


def _pointer(collection: str, element_id: str) -> str:
    return f"/{collection}/{element_id}"


def check_references(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
    data = body.data
    index = package_index(data)
    diagnostics: list[Diagnostic] = []
    source_uri = body.source_path or None
    # Solution packages may realize enterprise conceptual entities that live
    # outside this ModelPackage (ADR-021 conceptual_implementation_ref).
    external_ok: set[str] = set()
    if data.get("conceptual_implementation_ref"):
        for mapping in data.get("mappings") or []:
            if not isinstance(mapping, dict):
                continue
            if mapping.get("mapping_type") != "realizes":
                continue
            for ref in mapping.get("target_refs") or []:
                external_ok.add(str(ref))
        for entity in data.get("logical_entities") or []:
            if not isinstance(entity, dict):
                continue
            for cref in entity.get("conceptual_entity_refs") or []:
                s = str(cref)
                if s.startswith("dams:concept/") and s in external_ok:
                    continue
                # Also allow dams:concept/* when enterprise ref is declared
                if s.startswith("dams:concept/"):
                    external_ok.add(s)

    def require(
        ref: str | None,
        *,
        subject: str | None,
        collection: str,
        code: str,
        label: str,
    ) -> None:
        if not ref:
            return
        key = str(ref)
        if key in index or key in external_ok:
            return
        diagnostics.append(
            Diagnostic(
                diagnostic_code=code,
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message=f"Unresolved {label}: {ref}",
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=subject,
                source_location=SourceLocation(
                    source_uri=source_uri,
                    json_pointer=_pointer(collection, subject or ""),
                )
                if subject
                else (
                    SourceLocation(source_uri=source_uri) if source_uri else None
                ),
            )
        )

    for entity in data.get("logical_entities") or []:
        if not isinstance(entity, dict):
            continue
        eid = str(entity.get("element_id") or "")
        for cref in entity.get("conceptual_entity_refs") or []:
            require(
                str(cref),
                subject=eid,
                collection="logical_entities",
                code="DAMS-REF-001",
                label="conceptual_entity_ref",
            )
        require(
            entity.get("context_ref"),
            subject=eid,
            collection="logical_entities",
            code="DAMS-REF-002",
            label="context_ref",
        )

    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        rid = str(rel.get("element_id") or "")
        require(
            rel.get("source_entity_ref"),
            subject=rid,
            collection="relationships",
            code="DAMS-REF-005",
            label="source_entity_ref",
        )
        require(
            rel.get("target_entity_ref"),
            subject=rid,
            collection="relationships",
            code="DAMS-REF-006",
            label="target_entity_ref",
        )

    for mapping in data.get("mappings") or []:
        if not isinstance(mapping, dict):
            continue
        mid = str(mapping.get("element_id") or "")
        sources = mapping.get("source_refs") or []
        targets = mapping.get("target_refs") or []
        if not sources or not targets:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-REF-003",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "Mapping must have at least one source_refs and target_refs"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=mid or None,
                    source_location=SourceLocation(
                        source_uri=source_uri,
                        json_pointer=_pointer("mappings", mid),
                    )
                    if mid
                    else (SourceLocation(source_uri=source_uri) if source_uri else None),
                    diagnostic_details=(
                        DiagnosticDetail(
                            detail_key="suggestion",
                            detail_value="Add at least one source_refs and target_refs",
                        ),
                    ),
                )
            )
        for ref in list(sources) + list(targets):
            sref = str(ref)
            # External IRIs on aligns_with are intentional (ADR-021).
            if (
                mapping.get("mapping_type") == "aligns_with"
                and (
                    sref.startswith("http://")
                    or sref.startswith("https://")
                )
            ):
                continue
            require(
                sref,
                subject=mid,
                collection="mappings",
                code="DAMS-REF-004",
                label="mapping endpoint",
            )

    return tuple(diagnostics)
