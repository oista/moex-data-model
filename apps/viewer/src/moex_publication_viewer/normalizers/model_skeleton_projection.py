"""Derive a ModelPackage-shaped skeleton YAML from requirements formal_checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Where each target_class nests inside ModelPackage instance YAML.
_CLASS_PATH: dict[str, tuple[str, ...]] = {
    "ModelPackage": (),
    "LogicalEntity": ("logical_entities",),
    "LogicalAttribute": ("logical_entities", "attributes"),
    "Relationship": ("relationships",),
    "PhysicalObject": ("physical_objects",),
    "PhysicalField": ("physical_objects", "physical_fields"),
    "Mapping": ("mappings",),
    "DomainContext": ("domain_contexts",),
    "ConceptualEntity": ("conceptual_entities",),
}

_PLACEHOLDER = "<required>"
_REF_PLACEHOLDER = "<must-resolve-in-package>"


def _placeholder_for(kind: str, slot: str) -> Any:
    if kind == "ref_resolves" or slot.endswith("_ref") or slot.endswith("_refs"):
        if slot.endswith("_refs") or kind == "slot_min_cardinality":
            return [_REF_PLACEHOLDER]
        return _REF_PLACEHOLDER
    if kind == "slot_min_cardinality":
        return [_PLACEHOLDER]
    if slot in ("required", "multivalued", "identifying", "associative"):
        return None
    return _PLACEHOLDER


def _ensure_list_item(parent: dict[str, Any], key: str) -> dict[str, Any]:
    items = parent.setdefault(key, [])
    if not isinstance(items, list):
        items = []
        parent[key] = items
    if not items:
        items.append({})
    first = items[0]
    if not isinstance(first, dict):
        first = {}
        items[0] = first
    return first


def _node_at(root: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any]:
    node = root
    for key in path:
        node = _ensure_list_item(node, key)
    return node


def project_model_skeleton_from_catalog(
    catalog_path: Path,
    *,
    output_rel: str,
    header_label: str,
) -> dict[str, str]:
    """
    Build a ModelPackage skeleton from formal_checks in a requirements catalog.

    Returns mapping of relative path -> YAML text. Empty if catalog missing/invalid.
    Skips ``custom`` checks (no instance slot to fill).
    """
    if not catalog_path.is_file():
        return {}
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}

    root: dict[str, Any] = {}
    # Collect slots per class (preserve insertion order, first kind wins for placeholder)
    by_class: dict[str, dict[str, str]] = {}
    for req in data.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        for check in req.get("formal_checks") or []:
            if not isinstance(check, dict):
                continue
            kind = str(check.get("kind") or "")
            target_class = str(check.get("target_class") or "")
            target_slot = str(check.get("target_slot") or "")
            if not target_class or target_class not in _CLASS_PATH:
                continue
            if kind not in (
                "slot_required",
                "slot_min_cardinality",
                "ref_resolves",
                "at_least_one_slots",
            ):
                continue
            if kind == "at_least_one_slots":
                for s in check.get("target_slots") or []:
                    slot = str(s)
                    if not slot:
                        continue
                    slots = by_class.setdefault(target_class, {})
                    if slot not in slots:
                        slots[slot] = "slot_required"
                continue
            target_slot = str(check.get("target_slot") or "")
            if not target_slot and kind != "ref_resolves":
                continue
            # ref_resolves without target_slot (path-only) — skip slot write
            if not target_slot:
                continue
            slots = by_class.setdefault(target_class, {})
            if target_slot not in slots:
                slots[target_slot] = kind

    for target_class, slots in by_class.items():
        node = _node_at(root, _CLASS_PATH[target_class])
        for slot, kind in slots.items():
            if slot not in node:
                node[slot] = _placeholder_for(kind, slot)

    header = (
        f"# Derived ModelPackage skeleton from {header_label} formal_checks.\n"
        "# Placeholders: <required> / <must-resolve-in-package>.\n"
        "# Not a LinkML schema — instance shape owners must satisfy.\n"
    )
    text = header + yaml.dump(
        root,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    return {output_rel: text}


def project_it_solution_model_skeleton(catalog_path: Path) -> dict[str, str]:
    """IT-solution skeleton (backward-compatible entry point)."""
    return project_model_skeleton_from_catalog(
        catalog_path,
        output_rel="requirements/minimal/it-solution-model.skeleton.yaml",
        header_label="IT-solution",
    )


def project_conceptual_model_skeleton(catalog_path: Path) -> dict[str, str]:
    """Enterprise-conceptual skeleton from conceptual-model requirements."""
    return project_model_skeleton_from_catalog(
        catalog_path,
        output_rel="requirements/minimal/conceptual-model.skeleton.yaml",
        header_label="conceptual-model",
    )
