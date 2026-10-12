"""Unified iteration over legacy and typed Mapping collections (ADR-046)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

TYPED_MAPPING_KEYS = (
    "realizes_mappings",
    "entity_physical_mappings",
    "field_mappings",
    "aligns_with_mappings",
)
LEGACY_MAPPING_KEY = "mappings"


def iter_mappings(data: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield mapping objects from legacy + typed ModelPackage collections.

    Stable order: typed keys in ``TYPED_MAPPING_KEYS`` order, then legacy
    ``mappings``. Deduplicate by ``element_id`` when the same id appears in
    both typed and legacy (prefer first occurrence: typed collections first
    so migrated data wins, then legacy). Skip non-dicts. Entries without
    ``element_id`` are always yielded (no dedupe key).
    """
    seen: set[str] = set()
    for key in (*TYPED_MAPPING_KEYS, LEGACY_MAPPING_KEY):
        for item in data.get(key) or []:
            if not isinstance(item, dict):
                continue
            eid = item.get("element_id")
            if eid is not None and str(eid):
                sid = str(eid)
                if sid in seen:
                    continue
                seen.add(sid)
            yield item
