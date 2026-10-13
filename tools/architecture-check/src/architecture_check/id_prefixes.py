"""ADR-052: concrete IdentifiedElement/ModelElement classes need id_prefixes (or allowlist)."""

from __future__ import annotations

from pathlib import Path

# Shrink-only. Growth requires amending ADR-052 § Allowlist.
# Snapshot at schema 4.1.0 (Wave D2).
ID_PREFIXES_ALLOWLIST: frozenset[str] = frozenset(
    {
        "AlignsWithMapping",
        "ConceptualDomain",
        "ConceptualEntity",
        "ConceptualProperty",
        "DataFlow",
        "DataFlowEntityBinding",
        "DataModelBinding",
        "DataType",
        "Dimension",
        "DomainContext",
        "EntityPhysicalMapping",
        "FieldMapping",
        "LogicalAttribute",
        "LogicalEntity",
        "Mapping",
        "Metric",
        "ModelPackage",
        "ModelSelection",
        "RealizesMapping",
        "RelationTerm",
        "Relationship",
        "SelectedAttribute",
        "SelectedEntity",
        "SpecificationRequirement",
        "ValueDomain",
    }
)


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


def _induced_id_prefixes(sv, cname: str) -> list[str]:
    cdef = sv.get_class(cname)
    prefixes = list(cdef.id_prefixes or [])
    if prefixes:
        return prefixes
    cur = cdef.is_a
    while cur:
        parent = sv.get_class(cur)
        if parent is None:
            break
        prefixes = list(parent.id_prefixes or [])
        if prefixes:
            return prefixes
        cur = parent.is_a
    return []


def check_id_prefixes(root: str | Path) -> list[str]:
    """Return errors for missing id_prefixes outside the ADR-052 allowlist."""
    from linkml_runtime.utils.schemaview import SchemaView

    root = Path(root)
    schema = _schema_path(root)
    if not schema.is_file():
        return [f"missing DAMS schema: {schema}"]

    sv = SchemaView(str(schema))
    errors: list[str] = []
    missing: list[str] = []
    for cname in sorted(sv.all_classes()):
        cdef = sv.get_class(cname)
        if cdef.abstract:
            continue
        ancs = set(sv.class_ancestors(cname, reflexive=True))
        if "IdentifiedElement" not in ancs and "ModelElement" not in ancs:
            continue
        if _induced_id_prefixes(sv, cname):
            continue
        missing.append(cname)
        if cname not in ID_PREFIXES_ALLOWLIST:
            errors.append(
                f"{cname}: concrete IdentifiedElement/ModelElement lacks "
                f"id_prefixes; add prefixes or amend ADR-052 allowlist"
            )

    stale = sorted(ID_PREFIXES_ALLOWLIST - set(missing))
    for cname in stale:
        errors.append(
            f"{cname}: in ID_PREFIXES_ALLOWLIST but already has induced "
            f"id_prefixes; remove from allowlist (ADR-052 shrink-only)"
        )

    unknown = sorted(set(missing) - ID_PREFIXES_ALLOWLIST)
    # unknown already reported above as errors; keep list for clarity
    _ = unknown
    return sorted(errors)
