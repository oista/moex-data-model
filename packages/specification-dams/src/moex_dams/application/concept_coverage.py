"""Coverage metrics for ConceptualProperty linkage (informational, ADR-034 §3.7)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def compute_concept_coverage(packages: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute coverage report across one or more ModelPackage bodies.

    Does not raise; intended for CLI/viewer, never blocks make check.
    """
    total_attrs = 0
    with_concept = 0
    critical_without: list[str] = []
    props_referenced: set[str] = set()
    all_props: dict[str, dict[str, Any]] = {}
    name_type: dict[tuple[str, str], list[str]] = defaultdict(list)

    for data in packages:
        if not isinstance(data, dict):
            continue
        for prop in data.get("conceptual_properties") or []:
            if isinstance(prop, dict) and prop.get("element_id"):
                all_props[str(prop["element_id"])] = prop
        sol = str(data.get("solution_ref") or data.get("name") or "")
        for ent in data.get("logical_entities") or []:
            if not isinstance(ent, dict):
                continue
            for attr in ent.get("attributes") or []:
                if not isinstance(attr, dict):
                    continue
                total_attrs += 1
                aid = str(attr.get("element_id") or "")
                cref = str(attr.get("concept_ref") or "").strip()
                if cref:
                    with_concept += 1
                    props_referenced.add(cref)
                if attr.get("critical_data_element") is True and not cref:
                    critical_without.append(aid)
                nm = str(attr.get("name") or "")
                lt = str(attr.get("data_type_ref") or "")
                if nm and lt and sol:
                    name_type[(nm, lt)].append(aid)

    orphan_props = sorted(set(all_props) - props_referenced)
    cross_candidates = [
        {"name": n, "type": t, "attributes": ids}
        for (n, t), ids in sorted(name_type.items())
        if len(ids) >= 2
    ]

    ratio = (with_concept / total_attrs) if total_attrs else 0.0
    return {
        "attribute_count": total_attrs,
        "with_concept_ref": with_concept,
        "concept_ref_ratio": round(ratio, 4),
        "critical_without_concept_ref": critical_without,
        "orphan_conceptual_properties": orphan_props,
        "cross_solution_candidates": cross_candidates,
    }
