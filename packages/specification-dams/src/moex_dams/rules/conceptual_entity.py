"""ADR-026 checks for ConceptualEntity tier, dependency graph, and genesis."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody

EXACT_MATCH_KINDS = frozenset({"exact", "equivalent"})


def _diag(
    code: str,
    severity: DiagnosticSeverity,
    message: str,
    subject: str | None,
    *,
    remediation: str | None = None,
) -> Diagnostic:
    parts = [message]
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if remediation and str(remediation).strip():
        parts.append(f"Remediation: {remediation}")
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation).strip(),
            )
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def _concept_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for el in data.get("conceptual_entities") or []:
        if not isinstance(el, dict):
            continue
        eid = str(el.get("element_id") or "")
        if eid:
            out[eid] = el
    return out


def _rel_pairs(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rel in data.get("relationships") or []:
        if isinstance(rel, dict):
            out.append(rel)
    return out


def _has_mandatory_link(
    dependent: str,
    owner: str,
    relationships: list[dict[str, Any]],
) -> bool:
    """True if a Relationship requires ``dependent`` to reference ``owner``."""
    for rel in relationships:
        s = str(rel.get("source_entity_ref") or "")
        t = str(rel.get("target_entity_ref") or "")
        identifying = rel.get("identifying") is True
        if s == dependent and t == owner:
            try:
                mn = int(rel.get("source_min_cardinality") or 0)
            except (TypeError, ValueError):
                mn = 0
            if mn >= 1 or identifying:
                return True
        if s == owner and t == dependent and identifying:
            return True
    return False


def _find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    """Return list of cycles (each as list of node ids) in directed depends_on graph."""
    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            if node in path:
                idx = path.index(node)
                cycles.append(path[idx:] + [node])
            return
        visiting.add(node)
        path.append(node)
        for nxt in edges.get(node, []):
            dfs(nxt)
        path.pop()
        visiting.remove(node)
        visited.add(node)

    for n in edges:
        dfs(n)
    return cycles


def check_conceptual_entities(data: dict[str, Any]) -> list[Diagnostic]:
    """Validate entity_tier / dependency_kind / genesis_kind (ADR-026)."""
    out: list[Diagnostic] = []
    concepts = _concept_map(data)
    relationships = _rel_pairs(data)
    dep_edges: dict[str, list[str]] = {eid: [] for eid in concepts}

    for eid, el in concepts.items():
        tier = el.get("entity_tier")
        dep_kind = el.get("dependency_kind")
        depends = [
            str(r) for r in (el.get("depends_on_refs") or []) if r
        ]
        genesis = el.get("genesis_kind")
        ext_refs = el.get("external_class_refs") or []
        if not isinstance(ext_refs, list):
            ext_refs = []

        # Tier consistency
        if tier == "primary":
            if depends:
                out.append(
                    _diag(
                        "DAMS-CM-TIER-001",
                        DiagnosticSeverity.ERROR,
                        (
                            f'ConceptualEntity "{eid}" is primary but declares '
                            f"depends_on_refs={depends!r}."
                        ),
                        eid,
                        remediation="Clear depends_on_refs or set entity_tier=dependent.",
                    )
                )
            if dep_kind:
                out.append(
                    _diag(
                        "DAMS-CM-TIER-002",
                        DiagnosticSeverity.WARNING,
                        (
                            f'ConceptualEntity "{eid}" is primary but declares '
                            f"dependency_kind={dep_kind!r}."
                        ),
                        eid,
                        remediation="Omit dependency_kind for primary entities.",
                    )
                )
        elif tier == "dependent":
            if not depends:
                out.append(
                    _diag(
                        "DAMS-CM-TIER-003",
                        DiagnosticSeverity.ERROR,
                        (
                            f'ConceptualEntity "{eid}" is dependent but has no '
                            "depends_on_refs."
                        ),
                        eid,
                        remediation="List at least one owner in depends_on_refs.",
                    )
                )
            if not dep_kind:
                out.append(
                    _diag(
                        "DAMS-CM-TIER-004",
                        DiagnosticSeverity.ERROR,
                        (
                            f'ConceptualEntity "{eid}" is dependent but missing '
                            "dependency_kind (characteristic|associative)."
                        ),
                        eid,
                        remediation="Set dependency_kind per ADR-026.",
                    )
                )
            for owner in depends:
                if owner not in concepts:
                    out.append(
                        _diag(
                            "DAMS-CM-TIER-005",
                            DiagnosticSeverity.ERROR,
                            (
                                f'ConceptualEntity "{eid}" depends_on_refs entry '
                                f"{owner!r} is not a conceptual entity in this package."
                            ),
                            eid,
                        )
                    )
                else:
                    dep_edges[eid].append(owner)
                if owner in concepts and not _has_mandatory_link(
                    eid, owner, relationships
                ):
                    out.append(
                        _diag(
                            "DAMS-CM-TIER-006",
                            DiagnosticSeverity.WARNING,
                            (
                                f'ConceptualEntity "{eid}" depends on "{owner}" but '
                                "no mandatory Relationship (min_cardinality>=1 or "
                                "identifying) backs that dependency."
                            ),
                            eid,
                            remediation=(
                                "Add an identifying/mandatory Relationship to the "
                                "owner (ADR-026)."
                            ),
                        )
                    )
        elif tier is not None:
            out.append(
                _diag(
                    "DAMS-CM-TIER-007",
                    DiagnosticSeverity.ERROR,
                    f'ConceptualEntity "{eid}" has unknown entity_tier={tier!r}.',
                    eid,
                )
            )

        # Genesis consistency
        has_ext = any(
            isinstance(r, dict) and r.get("target_ref") for r in ext_refs
        )
        if genesis == "external" and not has_ext:
            out.append(
                _diag(
                    "DAMS-CM-GENESIS-001",
                    DiagnosticSeverity.ERROR,
                    (
                        f'ConceptualEntity "{eid}" has genesis_kind=external but '
                        "no external_class_refs."
                    ),
                    eid,
                    remediation="Add at least one ExternalClassRef or set genesis_kind=native.",
                )
            )
        elif genesis == "native" and has_ext:
            out.append(
                _diag(
                    "DAMS-CM-GENESIS-002",
                    DiagnosticSeverity.ERROR,
                    (
                        f'ConceptualEntity "{eid}" has genesis_kind=native but '
                        "declares external_class_refs."
                    ),
                    eid,
                    remediation="Clear external_class_refs or set genesis_kind=external.",
                )
            )
        elif genesis is None and has_ext:
            out.append(
                _diag(
                    "DAMS-CM-GENESIS-003",
                    DiagnosticSeverity.WARNING,
                    (
                        f'ConceptualEntity "{eid}" has external_class_refs but '
                        "no genesis_kind (implied external)."
                    ),
                    eid,
                    remediation="Set genesis_kind=external explicitly (ADR-026).",
                )
            )

        for ref in ext_refs:
            if not isinstance(ref, dict):
                continue
            mk = ref.get("match_kind")
            sk = ref.get("source_kind")
            tr = ref.get("target_ref")
            rid = str(ref.get("external_class_ref_id") or tr or eid)
            if not tr:
                out.append(
                    _diag(
                        "DAMS-CM-GENESIS-004",
                        DiagnosticSeverity.ERROR,
                        f'ExternalClassRef "{rid}" on "{eid}" missing target_ref.',
                        eid,
                    )
                )
            if not mk:
                out.append(
                    _diag(
                        "DAMS-CM-GENESIS-005",
                        DiagnosticSeverity.ERROR,
                        f'ExternalClassRef "{rid}" on "{eid}" missing match_kind.',
                        eid,
                    )
                )
            if not sk:
                out.append(
                    _diag(
                        "DAMS-CM-GENESIS-006",
                        DiagnosticSeverity.ERROR,
                        f'ExternalClassRef "{rid}" on "{eid}" missing source_kind.',
                        eid,
                    )
                )

    for cycle in _find_cycles(dep_edges):
        out.append(
            _diag(
                "DAMS-CM-TIER-008",
                DiagnosticSeverity.ERROR,
                f"depends_on cycle detected: {' -> '.join(cycle)}",
                cycle[0] if cycle else None,
                remediation="Remove a depends_on_refs edge to break the cycle.",
            )
        )

    # Warning: Mapping(aligns_with) disagreeing with external_class_refs
    concept_targets: dict[str, set[str]] = {}
    for eid, el in concepts.items():
        targets: set[str] = set()
        for ref in el.get("external_class_refs") or []:
            if isinstance(ref, dict) and ref.get("target_ref"):
                targets.add(str(ref["target_ref"]))
        concept_targets[eid] = targets

    for mapping in data.get("mappings") or []:
        if not isinstance(mapping, dict):
            continue
        if str(mapping.get("mapping_type") or "") != "aligns_with":
            continue
        sources = [str(s) for s in (mapping.get("source_refs") or []) if s]
        targets = [str(t) for t in (mapping.get("target_refs") or []) if t]
        mid = str(mapping.get("element_id") or mapping.get("name") or "")
        for src in sources:
            if src not in concept_targets:
                continue
            declared = concept_targets[src]
            if not declared:
                continue
            for tgt in targets:
                if tgt not in declared:
                    out.append(
                        _diag(
                            "DAMS-CM-GENESIS-007",
                            DiagnosticSeverity.WARNING,
                            (
                                f'Mapping "{mid}" aligns_with {tgt!r} for "{src}" '
                                "but that target is absent from external_class_refs "
                                "(ADR-026 canonical store)."
                            ),
                            src,
                            remediation=(
                                "Add ExternalClassRef on the ConceptualEntity or "
                                "update the Mapping."
                            ),
                        )
                    )

    return out


def check_conceptual_entities_body(
    body: LinkMLImplementationBody,
) -> tuple[Diagnostic, ...]:
    return tuple(check_conceptual_entities(body.data))


def match_kind_is_exact(match_kind: str | None) -> bool:
    """True when match_kind allows definition inheritance (ADR-025/026)."""
    return str(match_kind or "") in EXACT_MATCH_KINDS


def match_kind_for_target(
    element: dict[str, Any], target_ref: str
) -> str | None:
    """Return declared match_kind for target_ref, or None if undeclared."""
    for ref in element.get("external_class_refs") or []:
        if not isinstance(ref, dict):
            continue
        if str(ref.get("target_ref") or "") == target_ref:
            mk = ref.get("match_kind")
            return str(mk) if mk is not None else None
    return None
