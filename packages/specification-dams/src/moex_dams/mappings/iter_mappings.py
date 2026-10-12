"""Unified iteration over typed Mapping collections (ADR-046)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

TYPED_MAPPING_KEYS = (
    "realizes_mappings",
    "entity_physical_mappings",
    "field_mappings",
    "aligns_with_mappings",
)


def iter_mappings_with_collection(
    data: dict[str, Any],
) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield ``(collection_key, mapping)`` from typed ModelPackage collections.

    Stable order: typed keys in ``TYPED_MAPPING_KEYS`` order. Deduplicate by
    ``element_id`` when the same id appears in more than one collection
    (prefer first occurrence). Skip non-dicts. Entries without ``element_id``
    are always yielded (no dedupe key).

    Legacy polymorphic ``mappings`` is no longer read (removed in ADR-046 PR-5).
    """
    seen: set[str] = set()
    for key in TYPED_MAPPING_KEYS:
        for item in data.get(key) or []:
            if not isinstance(item, dict):
                continue
            eid = item.get("element_id")
            if eid is not None and str(eid):
                sid = str(eid)
                if sid in seen:
                    continue
                seen.add(sid)
            yield key, item


def iter_mappings(data: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield mapping objects from typed ModelPackage collections.

    Same order and deduplication as :func:`iter_mappings_with_collection`.
    """
    for _key, item in iter_mappings_with_collection(data):
        yield item
