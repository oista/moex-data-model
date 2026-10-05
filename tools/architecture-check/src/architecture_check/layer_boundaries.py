"""Schema-level layer boundary checks for DAMS modules (ADR-034 / §5)."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

# Conceptual classes must not declare slots whose range is logical/physical/technical.
CONCEPTUAL_CLASSES = frozenset(
    {
        "ConceptualEntity",
        "ConceptualProperty",
        "ConceptualDomain",
        "ValueMeaning",
        "RelationTerm",
    }
)
FORBIDDEN_RANGES_FROM_CONCEPTUAL = frozenset(
    {
        "LogicalEntity",
        "LogicalAttribute",
        "SchemaNode",
        "TechnicalAsset",
        "DataCarrier",
        "AccessPoint",
        "DataContainer",
        "ExecutionAsset",
        "DataFlow",
        "DataModelBinding",
    }
)

ENTERPRISE_ONLY_CLASSES = frozenset(
    {"ConceptualProperty", "ConceptualDomain", "ValueMeaning", "DataType", "NativeTypeBinding"}
)


def check_layer_boundaries(schema_path: str | Path) -> list[str]:
    """Return human-readable violations of conceptual→logical/physical refs."""
    sv = SchemaView(str(schema_path))
    errors: list[str] = []

    for cname in CONCEPTUAL_CLASSES:
        if cname not in sv.all_classes():
            continue
        for sname in sv.class_slots(cname):
            slot = sv.induced_slot(sname, cname)
            rng = slot.range
            if rng in FORBIDDEN_RANGES_FROM_CONCEPTUAL:
                errors.append(
                    f"{cname}.{sname} range={rng} violates conceptual→downward layer rule"
                )

    # Enterprise-only classes must exist (schema presence gate)
    for cname in ENTERPRISE_ONLY_CLASSES:
        if cname not in sv.all_classes():
            errors.append(f"missing expected enterprise-layer class: {cname}")

    # DataType registry classes must not reference LogicalAttribute
    for cname in ("DataType", "ValueDomain", "NativeTypeBinding"):
        if cname not in sv.all_classes():
            continue
        for sname in sv.class_slots(cname):
            slot = sv.induced_slot(sname, cname)
            if slot.range in {"LogicalAttribute", "LogicalEntity", "SchemaNode"}:
                errors.append(f"{cname}.{sname} must not range to {slot.range}")

    return sorted(errors)
