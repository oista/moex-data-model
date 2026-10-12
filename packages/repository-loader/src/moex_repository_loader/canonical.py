"""Canonical content hashing (same algorithm idea as ADR-042)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

_SKIP_DESCRIPTOR_KEYS = frozenset({"content_digest", "revision"})


def canonical_digest(payload: Any, *, skip_keys: frozenset[str] | None = None) -> str:
    """Return ``sha256:<hex>`` over canonical JSON of *payload*."""
    data = payload
    if skip_keys and isinstance(payload, dict):
        data = {k: v for k, v in payload.items() if k not in skip_keys}
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_content_hash(descriptor: dict[str, Any], body: dict[str, Any]) -> str:
    """Hash implementation envelope (without stamps) + parsed body."""
    clean_descriptor = {
        k: v for k, v in descriptor.items() if k not in _SKIP_DESCRIPTOR_KEYS
    }
    return canonical_digest({"descriptor": clean_descriptor, "body": body})
