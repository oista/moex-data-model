"""Canonical form of vertical_slice.json for freshness checks.

Only time-like fields are ignored. Content digests and revisions must match:
a stale body digest is a failed freshness check.
"""

from __future__ import annotations

import json
from typing import Any

VOLATILE_KEYS = frozenset(
    {
        "assessed_at",
        "generated_at",
        "timestamp",
        "created_at",
        "updated_at",
        "built_at",
    }
)


def strip_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: strip_volatile(v)
            for k, v in value.items()
            if k not in VOLATILE_KEYS
        }
    if isinstance(value, list):
        return [strip_volatile(v) for v in value]
    return value


def canonical_slice_json(data: Any) -> str:
    """Stable JSON string used to compare committed vs regenerated slices."""
    return json.dumps(
        strip_volatile(data),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )


def slices_equal(left: Any, right: Any) -> bool:
    return canonical_slice_json(left) == canonical_slice_json(right)
