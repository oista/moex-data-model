"""Project SliceResult → PublicationModule and viewer-friendly JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moex_dams.application.assess import SliceResult, assess_implementation
from moex_modeling.assets.domain import slug_and_version_from_id

from moex_publication.domain.read_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)


def build_publication_module(result: SliceResult) -> PublicationModule:
    """In-memory PublicationModule derived from a vertical-slice result."""
    report = result.report
    graph = result.graph
    impl = result.implementation

    summary_items = (
        PublicationItem(
            id="overall_result",
            title="overall_result",
            attributes={"value": report.overall_result.value},
        ),
        PublicationItem(
            id="implementation_id",
            title="implementation_id",
            attributes={"value": impl.id},
        ),
        PublicationItem(
            id="revision",
            title="revision",
            attributes={"value": impl.revision},
        ),
        PublicationItem(
            id="content_digest",
            title="content_digest",
            attributes={"value": impl.content_digest},
        ),
        PublicationItem(
            id="nodes",
            title="nodes",
            attributes={"value": len(graph.nodes)},
        ),
        PublicationItem(
            id="edges",
            title="edges",
            attributes={"value": len(graph.edges)},
        ),
    )

    node_items = tuple(
        PublicationItem(
            id=n.id,
            title=n.title or n.name or n.id,
            description=n.description,
            attributes={"kind": n.kind.value, "name": n.name},
        )
        for n in graph.nodes
    )

    diag_items = tuple(
        PublicationItem(
            id=f"{d.diagnostic_code}:{i}",
            title=d.diagnostic_code,
            description=d.diagnostic_message,
            attributes={
                "severity": d.severity.value,
                "phase": d.conformance_phase.value if d.conformance_phase else None,
                "subject_ref": d.subject_ref,
            },
        )
        for i, d in enumerate(
            diag for a in report.assessments for diag in a.diagnostics
        )
    )

    relation_items = tuple(
        PublicationItem(
            id=f"{r.relation_kind.value}:{r.relation_source}->{r.relation_target}",
            title=r.relation_kind.value,
            attributes={
                "source": r.relation_source,
                "target": r.relation_target,
            },
        )
        for r in result.universe.relations
    )

    try:
        impl_slug, _ = slug_and_version_from_id(impl.id)
    except ValueError:
        impl_slug = impl.id
    slice_label = impl.name or impl_slug

    return PublicationModule(
        module_id="moex:module:vertical-slice",
        title=f"Vertical slice ({slice_label})",
        description=(
            "Conformance report and DamsModelGraphView projected from "
            f"linkml → dams → {impl_slug}"
        ),
        icon="📐",
        version=impl.version,
        order=350,
        sections=(
            PublicationSection(
                id="summary",
                title="Slice summary",
                type="key-value",
                items=summary_items,
            ),
            PublicationSection(
                id="graph-nodes",
                title="Graph nodes",
                type="entity-table",
                columns=("kind", "name"),
                filterable=("kind",),
                items=node_items,
            ),
            PublicationSection(
                id="diagnostics",
                title="Diagnostics",
                type="entity-table",
                columns=("severity", "phase", "subject_ref"),
                filterable=("severity",),
                items=diag_items,
                default_collapsed=not diag_items,
            ),
            PublicationSection(
                id="relations",
                title="Universe relations",
                type="entity-table",
                columns=("source", "target"),
                items=relation_items,
            ),
        ),
    )


def _bundle_digest() -> str | None:
    """Best-effort read of committed DAMS release bundle digest."""
    # …/packages/publication/src/moex_publication/application/this.py → repo root
    root = Path(__file__).resolve().parents[5]
    manifest = root / "generated" / "manifests" / "moex-dams-bundle.json"
    if not manifest.is_file():
        return None
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("content_digest")
    except (OSError, json.JSONDecodeError):
        return None


def build_slice_projection(result: SliceResult) -> dict[str, Any]:
    """Flat JSON projection for root viewer json_normalizer + select paths."""
    report = result.report
    graph = result.graph
    impl = result.implementation
    summary = {
        "overall_result": report.overall_result.value,
        "implementation_id": impl.id,
        "revision": impl.revision,
        "content_digest": impl.content_digest,
        "package_id": graph.package_id,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "is_conformant": report.is_conformant,
    }
    bundle = _bundle_digest()
    if bundle:
        summary["bundle_digest"] = bundle

    def _detail_map(d: Any) -> dict[str, str | None]:
        return {
            det.detail_key: det.detail_value
            for det in (d.diagnostic_details or ())
        }

    model_req = next(
        (a for a in report.assessments if a.id == "assessment:model-requirements"),
        None,
    )
    model_assessment: list[dict[str, Any]] = []
    if model_req is not None:
        for i, d in enumerate(model_req.diagnostics):
            details = _detail_map(d)
            sev = d.severity.value if d.severity else "error"
            status = "warn" if sev == "warning" else "fail"
            loc = None
            if d.source_location is not None:
                loc = getattr(d.source_location, "json_pointer", None) or getattr(
                    d.source_location, "source_uri", None
                )
            if not loc and d.subject_ref:
                loc = d.subject_ref
            model_assessment.append(
                {
                    "id": f"{d.diagnostic_code}:{i}",
                    "status": status,
                    "requirement_code": details.get("requirement_code"),
                    "statement": details.get("statement"),
                    "subject": d.subject_ref,
                    "finding": details.get("finding") or d.diagnostic_message,
                    "severity": sev,
                    "remediation": details.get("remediation"),
                    "source_location": loc,
                    "diagnostic_code": d.diagnostic_code,
                }
            )

    return {
        "summary": summary,
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "title": n.title,
                "description": n.description,
                "kind": n.kind.value,
            }
            for n in graph.nodes
        ],
        "edges": [
            {
                "id": f"{e.source}->{e.target}:{e.kind.value}",
                "source": e.source,
                "target": e.target,
                "kind": e.kind.value,
            }
            for e in graph.edges
        ],
        "diagnostics": [
            {
                "id": f"{d.diagnostic_code}:{i}",
                "code": d.diagnostic_code,
                "severity": d.severity.value,
                "phase": d.conformance_phase.value if d.conformance_phase else None,
                "message": d.diagnostic_message,
                "subject_ref": d.subject_ref,
            }
            for i, d in enumerate(
                diag for a in report.assessments for diag in a.diagnostics
            )
        ],
        "model_assessment": model_assessment,
        "relations": [
            {
                "id": f"{r.relation_kind.value}:{i}",
                "kind": r.relation_kind.value,
                "source": r.relation_source,
                "target": r.relation_target,
            }
            for i, r in enumerate(result.universe.relations)
        ],
        "module": build_publication_module(result).model_dump(mode="json"),
    }


def export_slice_projection(
    *,
    schema_path: Path | str,
    implementation_path: Path | str,
    out_path: Path | str,
    implementation_id: str | None = None,
) -> SliceResult:
    """Assess implementation and write viewer JSON projection."""
    result = assess_implementation(
        schema_path=schema_path,
        implementation_path=implementation_path,
        implementation_id=implementation_id,
    )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build_slice_projection(result)
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result
