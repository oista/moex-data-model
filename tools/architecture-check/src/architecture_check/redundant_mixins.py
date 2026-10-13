"""ADR-044: flag mixins re-declared when already induced via is_a or sibling mixins."""

from __future__ import annotations

from pathlib import Path


def _schema_path(root: Path) -> Path:
    return (
        root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
        / "moex-dams.yaml"
    )


def _mixins_induced_via_isa(sv, cname: str) -> set[str]:
    """Mixins induced by the is_a parent chain (not the class's own mixins list)."""
    induced: set[str] = set()
    cur = sv.get_class(cname).is_a
    while cur:
        cdef = sv.get_class(cur)
        if cdef is None:
            break
        for m in cdef.mixins or []:
            induced.add(m)
            for mm in sv.class_ancestors(m, reflexive=False):
                induced.add(mm)
        cur = cdef.is_a
    return induced


def check_redundant_mixins(root: str | Path) -> list[str]:
    """Return errors for mixins already inherited via is_a or another declared mixin."""
    from linkml_runtime.utils.schemaview import SchemaView

    root = Path(root)
    schema = _schema_path(root)
    if not schema.is_file():
        return [f"missing DAMS schema: {schema}"]

    sv = SchemaView(str(schema))
    errors: list[str] = []
    for cname in sorted(sv.all_classes()):
        cdef = sv.get_class(cname)
        declared = list(cdef.mixins or [])
        if not declared:
            continue
        via_isa = _mixins_induced_via_isa(sv, cname)
        for m in declared:
            if m in via_isa:
                errors.append(
                    f"{cname}: mixin {m} is already induced via is_a "
                    f"(parent {cdef.is_a}); remove redundant declaration (ADR-044)"
                )
        for m in declared:
            for other in declared:
                if other == m:
                    continue
                if m in set(sv.class_ancestors(other, reflexive=False)):
                    errors.append(
                        f"{cname}: mixin {m} is already induced by sibling "
                        f"mixin {other}; remove redundant declaration (ADR-044)"
                    )
    return sorted(errors)
