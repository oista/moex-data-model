"""ADR-025/026 model glossary view builder (entities + relation terms)."""

from __future__ import annotations

from typing import Any

from moex_dams.rules.definitions import (
    DefinitionIndex,
    DefinitionMode,
    build_definition_index,
    resolve_definition,
)
from moex_dams.rules.relation_terms import relation_label


def build_model_glossary(
    body_data: dict[str, Any],
    *,
    index: DefinitionIndex | None = None,
) -> list[dict[str, Any]]:
    """Build a glossary *view* of ConceptualEntity and RelationTerm rows.

    Not a source of truth — derived from the model package via the ADR-025
    definition resolver (ADR-026 §5).
    """
    idx = index or build_definition_index(body_data)
    rows: list[dict[str, Any]] = []

    for el in body_data.get("conceptual_entities") or []:
        if not isinstance(el, dict):
            continue
        eid = str(el.get("element_id") or "")
        if not eid:
            continue
        prov = resolve_definition(el, idx, level="ConceptualEntity")
        ext_targets = []
        for cref in el.get("external_class_refs") or []:
            if isinstance(cref, dict) and cref.get("target_ref"):
                ext_targets.append(
                    {
                        "target_ref": str(cref["target_ref"]),
                        "match_kind": str(cref.get("match_kind") or ""),
                        "source_kind": str(cref.get("source_kind") or ""),
                    }
                )
        mode = prov.mode.value if isinstance(prov.mode, DefinitionMode) else str(prov.mode)
        rows.append(
            {
                "id": eid,
                "name": el.get("name") or eid,
                "title": el.get("title") or el.get("name") or eid,
                "description": prov.text or el.get("description") or "",
                "kind": "entity",
                "definition_mode": mode,
                "definition_source": prov.source_element_id,
                "entity_tier": el.get("entity_tier"),
                "dependency_kind": el.get("dependency_kind"),
                "genesis_kind": el.get("genesis_kind"),
                "aliases": el.get("aliases") or [],
                "external_class_refs": ext_targets,
                "label": el.get("title") or el.get("name") or eid,
                "definition": prov.text or el.get("description") or "",
            }
        )

    for term in body_data.get("relation_terms") or []:
        if not isinstance(term, dict):
            continue
        tid = str(term.get("element_id") or "")
        if not tid:
            continue
        prov = resolve_definition(term, idx, level="RelationTerm")
        mode = prov.mode.value if isinstance(prov.mode, DefinitionMode) else str(prov.mode)
        fwd = relation_label(term, direction="forward") or ""
        inv = relation_label(term, direction="inverse") or fwd
        rows.append(
            {
                "id": tid,
                "name": term.get("name") or tid,
                "title": term.get("title") or f"{fwd} / {inv}",
                "description": prov.text or term.get("description") or "",
                "kind": "relation-term",
                "definition_mode": mode,
                "definition_source": prov.source_element_id,
                "forward_label": fwd,
                "inverse_label": inv,
                "forward_label_en": term.get("forward_label_en"),
                "inverse_label_en": term.get("inverse_label_en"),
                "symmetric": bool(term.get("symmetric")),
                "aliases": term.get("aliases") or [],
                "label": term.get("title") or term.get("name") or tid,
                "definition": prov.text or term.get("description") or "",
            }
        )

    rows.sort(key=lambda r: str(r.get("title") or r.get("id") or "").lower())
    return rows
