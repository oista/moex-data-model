"""Semantic diff of two DAMS ModelPackage implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from moex_modeling import (
    ChangeCategory,
    DiagnosticDetail,
    ImplementationRef,
    SemanticChange,
    SemanticDiffReport,
)

from moex_dams.application.repository import DamsAssetRepository
from moex_dams.domain.graph import (
    DamsModelGraphView,
    EdgeKind,
    NodeKind,
)
from moex_dams.mappings.dams_to_graph import build_dams_graph, package_index

# Keys compared for property deltas (order matters for messaging).
_DOC_KEYS = frozenset({"description", "title", "name"})
_GOV_KEYS = frozenset({"governance_classification"})
_SKIP_KEYS = frozenset(
    {
        "element_id",
        "attributes",
        "physical_fields",
        "conceptual_entities",
        "logical_entities",
        "data_carriers",
        "access_points",
        "data_containers",
        "execution_assets",
        "domain_contexts",
        "mappings",
        "relationships",
        "conceptual_entity_refs",
        "key_attribute_refs",
        "source_refs",
        "target_refs",
        "source_entity_ref",
        "target_entity_ref",
        "sensitivity_term_refs",
    }
)

_REF_EDGE_KINDS = frozenset(
    {
        EdgeKind.MAPS_TO,
        EdgeKind.CONCEPTUAL_REF,
        EdgeKind.CARRIER_REF,
        EdgeKind.RELATES_TO,
    }
)

_PHYSICAL_KINDS = frozenset({NodeKind.TECHNICAL_ASSET, NodeKind.FIELD})


def diff_implementations(
    *,
    schema_path: Path | str,
    left_path: Path | str,
    right_path: Path | str,
    base_label: str | None = None,
    target_label: str | None = None,
) -> SemanticDiffReport:
    """Load two YAML bodies and classify semantic changes (no LinkML validate gate)."""
    schema_path = Path(schema_path)
    left_path = Path(left_path)
    right_path = Path(right_path)
    repo = DamsAssetRepository(
        default_schema_path=schema_path,
        default_target_class="ModelPackage",
    )
    left_ref = ImplementationRef(
        implementation_id=f"moex:implementation:{left_path.stem}",
        implementation_revision="left",
    )
    right_ref = ImplementationRef(
        implementation_id=f"moex:implementation:{right_path.stem}",
        implementation_revision="right",
    )
    left_body = repo.load_implementation(left_ref, path=left_path)
    right_body = repo.load_implementation(right_ref, path=right_path)
    left_graph = build_dams_graph(left_body)
    right_graph = build_dams_graph(right_body)
    return diff_graphs(
        left_graph,
        right_graph,
        left_index=package_index(left_body.data),
        right_index=package_index(right_body.data),
        base_label=base_label or left_path.name,
        target_label=target_label or right_path.name,
    )


def diff_graphs(
    left: DamsModelGraphView,
    right: DamsModelGraphView,
    *,
    left_index: dict[str, dict[str, Any]],
    right_index: dict[str, dict[str, Any]],
    base_label: str = "base",
    target_label: str = "target",
) -> SemanticDiffReport:
    changes: list[SemanticChange] = []
    left_ids = left.node_ids()
    right_ids = right.node_ids()
    left_by_id = {n.id: n for n in left.nodes}
    right_by_id = {n.id: n for n in right.nodes}

    for eid in sorted(right_ids - left_ids):
        node = right_by_id[eid]
        changes.append(
            SemanticChange(
                change_code="DAMS-DIFF-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=eid,
                message=f"Added {node.kind.value} {eid}",
                path=node.kind.value,
            )
        )

    for eid in sorted(left_ids - right_ids):
        node = left_by_id[eid]
        changes.append(
            SemanticChange(
                change_code="DAMS-DIFF-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=eid,
                message=f"Removed {node.kind.value} {eid}",
                path=node.kind.value,
            )
        )

    for eid in sorted(left_ids & right_ids):
        left_item = left_index.get(eid)
        right_item = right_index.get(eid)
        if left_item is None or right_item is None:
            continue
        changes.extend(
            _classify_item_delta(
                eid,
                left_item,
                right_item,
                kind=left_by_id[eid].kind,
            )
        )

    changes.extend(_classify_edge_deltas(left, right))

    report_id = f"semantic-diff:{base_label}:{target_label}"
    return SemanticDiffReport(
        id=report_id,
        base_label=base_label,
        target_label=target_label,
        changes=tuple(changes),
    )


def _classify_item_delta(
    eid: str,
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    kind: NodeKind,
) -> list[SemanticChange]:
    out: list[SemanticChange] = []

    left_req = left.get("required")
    right_req = right.get("required")
    if left_req is not None or right_req is not None:
        if left_req is False and right_req is True:
            out.append(
                SemanticChange(
                    change_code="DAMS-DIFF-REQUIRED",
                    category=ChangeCategory.BREAKING,
                    subject_ref=eid,
                    message=f"Property required changed false→true on {eid}",
                    path="required",
                    before=(DiagnosticDetail(detail_key="required", detail_value="false"),),
                    after=(DiagnosticDetail(detail_key="required", detail_value="true"),),
                )
            )
        elif left_req is True and right_req is False:
            out.append(
                SemanticChange(
                    change_code="DAMS-DIFF-OPTIONAL",
                    category=ChangeCategory.BACKWARD_COMPATIBLE,
                    subject_ref=eid,
                    message=f"Property required changed true→false on {eid}",
                    path="required",
                    before=(DiagnosticDetail(detail_key="required", detail_value="true"),),
                    after=(DiagnosticDetail(detail_key="required", detail_value="false"),),
                )
            )

    left_keys = set(left) - _SKIP_KEYS
    right_keys = set(right) - _SKIP_KEYS
    # required already handled
    left_keys.discard("required")
    right_keys.discard("required")

    changed = {
        k
        for k in left_keys | right_keys
        if _norm(left.get(k)) != _norm(right.get(k))
    }
    if not changed:
        return out

    if changed <= _DOC_KEYS:
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-DOC",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=eid,
                message=f"Documentation fields changed on {eid}: {sorted(changed)}",
                path=",".join(sorted(changed)),
            )
        )
        return out

    if changed & _GOV_KEYS:
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-GOV",
                category=ChangeCategory.GOVERNANCE,
                subject_ref=eid,
                message=f"Governance classification changed on {eid}",
                path="governance_classification",
                before=(
                    DiagnosticDetail(
                        detail_key="governance_classification",
                        detail_value=_str_or_none(left.get("governance_classification")),
                    ),
                ),
                after=(
                    DiagnosticDetail(
                        detail_key="governance_classification",
                        detail_value=_str_or_none(right.get("governance_classification")),
                    ),
                ),
            )
        )
        changed -= _GOV_KEYS
        changed -= _DOC_KEYS
        if not changed:
            return out

    if kind in _PHYSICAL_KINDS and changed:
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-PHYS",
                category=ChangeCategory.OPERATIONAL,
                subject_ref=eid,
                message=f"Physical properties changed on {eid}: {sorted(changed)}",
                path=",".join(sorted(changed)),
            )
        )
        return out

    # Remaining non-doc, non-gov property deltas — conservative breaking.
    remaining = changed - _DOC_KEYS
    if remaining:
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-PROP",
                category=ChangeCategory.BREAKING,
                subject_ref=eid,
                message=f"Properties changed on {eid}: {sorted(remaining)}",
                path=",".join(sorted(remaining)),
            )
        )
    elif changed & _DOC_KEYS:
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-DOC",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=eid,
                message=f"Documentation fields changed on {eid}: {sorted(changed & _DOC_KEYS)}",
                path=",".join(sorted(changed & _DOC_KEYS)),
            )
        )
    return out


def _classify_edge_deltas(
    left: DamsModelGraphView,
    right: DamsModelGraphView,
) -> list[SemanticChange]:
    def key(e: Any) -> tuple[str, str, str]:
        return (e.source, e.target, e.kind.value)

    left_edges = {key(e) for e in left.edges if e.kind in _REF_EDGE_KINDS}
    right_edges = {key(e) for e in right.edges if e.kind in _REF_EDGE_KINDS}
    out: list[SemanticChange] = []

    for source, target, kind in sorted(right_edges - left_edges):
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-EDGE-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=source,
                message=f"Added edge {kind} {source}→{target}",
                path=kind,
            )
        )
    for source, target, kind in sorted(left_edges - right_edges):
        out.append(
            SemanticChange(
                change_code="DAMS-DIFF-EDGE-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=source,
                message=f"Removed edge {kind} {source}→{target}",
                path=kind,
            )
        )
    return out


def _norm(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_norm(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _norm(v)) for k, v in value.items()))
    return value


def _str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
