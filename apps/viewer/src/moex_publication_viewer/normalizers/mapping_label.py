"""ADR-044 Mapping display label helpers."""

from __future__ import annotations


def mapping_display_label(mapping: dict) -> str:
    """Prefer source_refs -> target_refs [mapping_type]; fall back to name."""
    sources = mapping.get("source_refs") or []
    targets = mapping.get("target_refs") or []
    mtype = mapping.get("mapping_type")
    if sources or targets or mtype:
        src = ", ".join(str(x) for x in sources) if sources else "?"
        tgt = ", ".join(str(x) for x in targets) if targets else "?"
        kind = mtype or "?"
        return f"{src} -> {tgt} [{kind}]"
    name = mapping.get("name")
    if name:
        return str(name)
    eid = mapping.get("element_id")
    return str(eid) if eid else "Mapping"
