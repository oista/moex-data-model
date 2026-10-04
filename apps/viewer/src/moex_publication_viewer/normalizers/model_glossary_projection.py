"""Project a DAMS ModelPackage YAML into a model-glossary view (ADR-026).

Used when a publication section selects ``model_glossary`` from a YAML
ModelPackage body. Prefer pre-generated ``publications/model_glossary.json``
(built via ``moex_dams.rules.glossary.build_model_glossary``); this projection
is a lightweight fallback that does not depend on specification-dams at
viewer runtime.
"""

from __future__ import annotations

from typing import Any


def project_model_glossary(data: Any) -> list[dict[str, Any]]:
    """Build glossary rows from a ModelPackage dict without the ADR-025 resolver."""
    if not isinstance(data, dict):
        return []
    rows: list[dict[str, Any]] = []

    for el in data.get("conceptual_entities") or []:
        if not isinstance(el, dict):
            continue
        eid = str(el.get("element_id") or "")
        if not eid:
            continue
        desc = el.get("description")
        source = el.get("definition_source_ref")
        if isinstance(desc, str) and desc.strip():
            mode = "own_adapted" if source else "own"
            text = desc.strip()
        elif source:
            mode = "inherited"
            text = ""
        else:
            mode = "unresolved"
            text = ""
        row = {
            "id": eid,
            "name": el.get("name") or eid,
            "title": el.get("title") or el.get("name") or eid,
            "description": text,
            "kind": "entity",
            "definition_mode": mode,
            "definition_source": str(source) if source else None,
            "entity_tier": el.get("entity_tier"),
            "genesis_kind": el.get("genesis_kind"),
            "label": el.get("title") or el.get("name") or eid,
            "definition": text,
        }
        parent_ref = el.get("parent_concept_ref")
        if parent_ref:
            row["parent_concept_ref"] = str(parent_ref)
        rows.append(row)

    for term in data.get("relation_terms") or []:
        if not isinstance(term, dict):
            continue
        tid = str(term.get("element_id") or "")
        if not tid:
            continue
        fwd = str(term.get("forward_label") or "").strip()
        inv = str(term.get("inverse_label") or fwd).strip()
        desc = term.get("description")
        text = desc.strip() if isinstance(desc, str) and desc.strip() else ""
        rows.append(
            {
                "id": tid,
                "name": term.get("name") or tid,
                "title": term.get("title") or (f"{fwd} / {inv}" if fwd else tid),
                "description": text,
                "kind": "relation-term",
                "definition_mode": "own" if text else "unresolved",
                "forward_label": fwd,
                "inverse_label": inv,
                "symmetric": bool(term.get("symmetric")),
                "label": term.get("title") or term.get("name") or tid,
                "definition": text,
            }
        )

    rows.sort(key=lambda r: str(r.get("title") or r.get("id") or "").lower())
    return rows
