"""ADR-052: concrete IdentifiedElement/ModelElement classes need id_prefixes (or allowlist)."""

from __future__ import annotations

from pathlib import Path

# Shrink-only. Growth requires amending ADR-052 § id_prefixes allowlist.
# Ceiling is a ratchet: lower it (and never raise) when classes leave the set.
# Snapshot at schema 5.1.0 (audit R2-10).
ID_PREFIXES_ALLOWLIST: dict[str, str] = {
    "AlignsWithMapping": "mapping subclass; add dams with Mapping family (minor)",
    "ConceptualDomain": "semantic registry; add dams (minor)",
    "ConceptualEntity": "core semantic; add dams (minor)",
    "ConceptualProperty": "core semantic; add dams (minor)",
    "DataFlow": "integration root; add dams (minor)",
    "DataFlowEntityBinding": "exit on 6.0.0 (EmbeddedElement / slim id — ADR-052 D5)",
    "DataModelBinding": "contract binding; add dams (minor)",
    "DataType": "datatype registry; add dams (minor)",
    "Dimension": "analytics; add dams (minor)",
    "DomainContext": "package child; add dams (minor)",
    "EntityPhysicalMapping": "mapping subclass; add dams with Mapping family (minor)",
    "FieldMapping": "mapping subclass; add dams with Mapping family (minor)",
    "LogicalAttribute": "core logical; add dams (minor)",
    "LogicalEntity": "core logical; add dams (minor)",
    "Mapping": "abstract base still concrete for generators; add dams (minor)",
    "Metric": "analytics; add dams (minor)",
    "ModelPackage": "aggregate root; add dams (minor)",
    "ModelSelection": "exit on 6.0.0 (EmbeddedElement — ADR-052 D5)",
    "RealizesMapping": "mapping subclass; add dams with Mapping family (minor)",
    "RelationTerm": "semantic registry; add dams (minor)",
    "Relationship": "core logical; add dams (minor)",
    "SelectedAttribute": "exit on 6.0.0 (EmbeddedElement — ADR-052 D5)",
    "SelectedEntity": "exit on 6.0.0 (EmbeddedElement — ADR-052 D5)",
    "SpecificationRequirement": "requirements catalog; add dams (minor)",
    "ValueDomain": "semantic registry; add dams (minor)",
}

# Ratchet ceiling: must equal len(ID_PREFIXES_ALLOWLIST) and only decrease.
ID_PREFIXES_ALLOWLIST_CEILING: int = 25

_ALLOWLIST_MARKER = "## id_prefixes allowlist"


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

    errors: list[str] = []
    size = len(ID_PREFIXES_ALLOWLIST)
    if size != ID_PREFIXES_ALLOWLIST_CEILING:
        errors.append(
            f"ID_PREFIXES_ALLOWLIST size {size} must equal ratchet ceiling "
            f"{ID_PREFIXES_ALLOWLIST_CEILING}. When a class leaves the "
            f"allowlist, remove it and lower the ceiling in the same PR. "
            f"Raising the ceiling requires amending ADR-052 § id_prefixes "
            f"allowlist with an explicit debt note."
        )

    sv = SchemaView(str(schema))
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

    stale = sorted(set(ID_PREFIXES_ALLOWLIST) - set(missing))
    for cname in stale:
        errors.append(
            f"{cname}: in ID_PREFIXES_ALLOWLIST but already has induced "
            f"id_prefixes; remove from allowlist and lower the ceiling "
            f"(ADR-052 shrink-only)"
        )

    return sorted(errors)


def check_id_prefixes_allowlist_documented(root: str | Path) -> list[str]:
    """Every allowlist class must appear under ADR-052 § id_prefixes allowlist."""
    adr = Path(root) / "docs" / "adr" / "ADR-052-identity-and-versioning.md"
    if not adr.is_file():
        return [f"missing ADR-052: {adr}"]
    text = adr.read_text(encoding="utf-8")
    if _ALLOWLIST_MARKER not in text:
        return [
            f"ADR-052 must contain section '{_ALLOWLIST_MARKER}' listing "
            "ID_PREFIXES_ALLOWLIST keys"
        ]
    section = text.split(_ALLOWLIST_MARKER, 1)[1]
    next_h2 = section.find("\n## ")
    if next_h2 >= 0:
        section = section[:next_h2]
    missing = [
        name
        for name in ID_PREFIXES_ALLOWLIST
        if f"`{name}`" not in section
    ]
    if not missing:
        return []
    return [
        "ADR-052 allowlist section missing classes (amend ADR before growing "
        f"ID_PREFIXES_ALLOWLIST): {', '.join(sorted(missing))}"
    ]
