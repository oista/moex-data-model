"""Project LogicalEntity × conceptual_entity_refs into link rows.

Used when a solution publication section selects ``conceptual_entity_links``
from a ModelPackage YAML body. One row per (logical entity, concept ref) pair.
"""

from __future__ import annotations

from typing import Any


def project_conceptual_entity_links(data: Any) -> list[dict[str, Any]]:
    """Build link rows from logical_entities' conceptual_entity_refs."""
    if not isinstance(data, dict):
        return []
    rows: list[dict[str, Any]] = []
    for entity in data.get("logical_entities") or []:
        if not isinstance(entity, dict):
            continue
        logical_id = str(entity.get("element_id") or "")
        if not logical_id:
            continue
        refs = entity.get("conceptual_entity_refs") or []
        if not isinstance(refs, list) or not refs:
            continue
        logical_name = entity.get("name") or logical_id
        logical_title = entity.get("title") or logical_name
        alignment = entity.get("conceptual_alignment_status")
        rationale = entity.get("alignment_rationale")
        for ref in refs:
            concept_ref = str(ref)
            if not concept_ref:
                continue
            rows.append(
                {
                    "element_id": f"{logical_id}::{concept_ref}",
                    "logical_entity_ref": logical_id,
                    "logical_name": str(logical_name),
                    "logical_title": str(logical_title),
                    "conceptual_entity_ref": concept_ref,
                    "conceptual_alignment_status": (
                        str(alignment) if alignment is not None else None
                    ),
                    "alignment_rationale": (
                        str(rationale) if rationale is not None else None
                    ),
                }
            )
    return rows
