"""Compile ValueDomain permissible_values to LinkML enum YAML (ADR-035)."""

from __future__ import annotations

from typing import Any


def value_domain_to_linkml_enum(domain: dict[str, Any]) -> dict[str, Any] | None:
    """Return a LinkML enum fragment or None if domain is not enumerated."""
    if not isinstance(domain, dict):
        return None
    if str(domain.get("value_domain_kind") or "") != "enumerated":
        # dynamic_query → reachable_from
        dq = domain.get("dynamic_query")
        if isinstance(dq, dict) and dq.get("source_ontology"):
            name = str(domain.get("name") or domain.get("element_id") or "DynamicEnum")
            safe = "".join(ch if ch.isalnum() else "_" for ch in name) or "DynamicEnum"
            return {
                "enums": {
                    safe: {
                        "reachable_from": {
                            "source_ontology": dq.get("source_ontology"),
                            "source_nodes": list(dq.get("source_nodes") or []),
                            "relationship_types": list(dq.get("relationship_types") or []),
                            "include_self": bool(dq.get("include_self", True)),
                        }
                    }
                }
            }
        return None

    pvs = domain.get("permissible_values") or []
    if not pvs:
        return None
    name = str(domain.get("name") or domain.get("element_id") or "GeneratedEnum")
    safe = "".join(ch if ch.isalnum() else "_" for ch in name) or "GeneratedEnum"
    permissible: dict[str, Any] = {}
    for pv in pvs:
        if not isinstance(pv, dict):
            continue
        code = str(pv.get("value_code") or "").strip()
        if not code:
            continue
        entry: dict[str, Any] = {}
        if pv.get("value_label"):
            entry["text"] = str(pv["value_label"])
        if pv.get("meaning_term_ref"):
            entry["meaning"] = str(pv["meaning_term_ref"])
        if pv.get("value_definition"):
            entry["description"] = str(pv["value_definition"])
        permissible[code] = entry or None
    return {"enums": {safe: {"permissible_values": permissible}}}
