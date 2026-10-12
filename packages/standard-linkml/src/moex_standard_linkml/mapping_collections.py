"""Typed Mapping collections of a DAMS ModelPackage (ADR-046).

``moex_dams.mappings`` owns the canonical reader (``iter_mappings``). This
package cannot import ``moex_dams`` (dependency direction), so the same key
set lives here; ``tests/test_mapping_collections.py`` keeps both in sync.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

# mapping_type designator -> ModelPackage collection key
MAPPING_TYPE_TO_COLLECTION: dict[str, str] = {
    "realizes": "realizes_mappings",
    "entity_physical": "entity_physical_mappings",
    "field_mapping": "field_mappings",
    "aligns_with": "aligns_with_mappings",
}

TYPED_MAPPING_KEYS: tuple[str, ...] = tuple(MAPPING_TYPE_TO_COLLECTION.values())


def iter_package_mappings(package: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield mapping dicts from all typed collections (stable key order)."""
    for key in TYPED_MAPPING_KEYS:
        for item in package.get(key) or []:
            if isinstance(item, dict):
                yield item
