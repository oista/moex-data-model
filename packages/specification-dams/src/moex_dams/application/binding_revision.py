"""DataModelBinding integrity digest and revision policy (ADR-031 / ADR-037).

Rules:
- ``demo=True`` (fixtures): recompute ``integrity_digest`` in place; do not invent
  a new revision.
- ``demo=False`` (production / solution models): never overwrite digest of an
  existing immutable revision. Instead bump ``model_revision``, set
  ``compatibility_baseline_ref`` to the previous revision URI, and compute a
  digest for the *new* revision only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_binding_payload(binding: dict[str, Any]) -> str:
    """Stable JSON of selection content used for integrity_digest."""
    return json.dumps(
        {
            "element_id": binding.get("element_id"),
            "model_package_ref": binding.get("model_package_ref"),
            "model_version": binding.get("model_version"),
            "model_revision": binding.get("model_revision"),
            "selections": binding.get("selections") or [],
            "compatibility_mode": binding.get("compatibility_mode"),
        },
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def compute_integrity_digest(binding: dict[str, Any]) -> str:
    payload = canonical_binding_payload(binding)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def previous_revision_uri(binding: dict[str, Any], old_revision: str) -> str:
    eid = str(binding.get("element_id") or "dams:binding/unknown").rstrip("/")
    return f"{eid}/rev/{old_revision}"


def apply_binding_revision_policy(
    data: dict[str, Any],
    *,
    demo: bool = False,
    reason: str = "model-content-migration",
    new_revision: str | None = None,
) -> list[str]:
    """Apply digest/revision policy to every DataModelBinding in ``data``.

    Works on:
    - a ModelPackage body with ``data_model_bindings`` list
    - a standalone DataModelBinding document (has ``integrity_digest`` at root)

    Returns human-readable report lines.
    """
    lines: list[str] = []
    bindings = _iter_bindings(data)
    if not bindings:
        return lines

    for binding in bindings:
        eid = str(binding.get("element_id") or "")
        old_rev = str(binding.get("model_revision") or "").strip()
        if demo:
            digest = compute_integrity_digest(binding)
            binding["integrity_digest"] = digest
            lines.append(f"RECOMPUTED integrity_digest (demo) for {eid}")
            continue

        # Production: new immutable revision
        if not old_rev:
            old_rev = "unknown"
        baseline = previous_revision_uri(binding, old_rev)
        rev = new_revision or _derive_revision(binding, reason=reason)
        binding["compatibility_baseline_ref"] = baseline
        binding["model_revision"] = rev
        binding["integrity_digest"] = compute_integrity_digest(binding)
        lines.append(
            f"NEW_REVISION {eid}: model_revision={rev} "
            f"baseline={baseline} reason={reason}"
        )
    return lines


def _derive_revision(binding: dict[str, Any], *, reason: str) -> str:
    seed = canonical_binding_payload(binding) + "|" + reason
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _iter_bindings(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    # Standalone binding document
    if "integrity_digest" in data and "model_revision" in data:
        out.append(data)
    for b in data.get("data_model_bindings") or []:
        if isinstance(b, dict):
            out.append(b)
    return out
