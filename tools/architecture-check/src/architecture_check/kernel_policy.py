"""Enforce modeling-kernel.yaml extension_policy against provider-specific names."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

EXPECTED_POLICY = "standard-specific-bodies-live-in-provider-schemas"
FORBIDDEN_PREFIXES = ("LinkML", "OpenAPI", "OWL", "Shacl", "JsonSchema")
# Coordinate types and shared kernel names are allowed even if phrasing overlaps.
ALLOWLIST = {
    "StandardRef",
    "SpecificationRef",
    "ImplementationRef",
}


def _setting_value(settings: dict | None, key: str) -> str | None:
    if not settings:
        return None
    raw = settings.get(key)
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    # LinkML Setting may expose .setting_value or .value
    for attr in ("setting_value", "value"):
        value = getattr(raw, attr, None)
        if value is not None and not callable(value):
            return str(value)
    if isinstance(raw, dict):
        return raw.get("setting_value") or raw.get("value")
    return None


def check_extension_policy(schema_path: str | Path) -> list[str]:
    """Return names that violate extension_policy, or empty list if clean."""
    path = Path(schema_path)
    sv = SchemaView(str(path))
    policy = _setting_value(sv.schema.settings, "extension_policy")
    if policy != EXPECTED_POLICY:
        return [
            f"extension_policy expected {EXPECTED_POLICY!r}, got {policy!r}"
        ]

    violations: list[str] = []
    names = (
        list(sv.all_classes())
        + list(sv.all_slots())
        + list(sv.all_enums())
    )
    for name in names:
        if name in ALLOWLIST:
            continue
        if any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            violations.append(name)
    return sorted(set(violations))
