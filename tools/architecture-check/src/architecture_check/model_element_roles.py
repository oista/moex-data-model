"""ADR-044: at most one description declaration; slot_usage.description allowlist."""

from __future__ import annotations

from pathlib import Path

import yaml

# Do not grow without amending ADR-044.
DESCRIPTION_SLOT_USAGE_ALLOWLIST: dict[str, str] = {
    "HasDefinition": "canonical softened definition + skos:definition exact_mappings",
    "ModelPackage": "D1 required description",
    "DomainContext": "D1 required description",
    "TechnicalAsset": "quantum / CDE invariant required description",
    "ConceptualDomain": "preserve pre-ADR-044 required",
    "DataType": "preserve pre-ADR-044 required",
    "ValueDomain": "preserve pre-ADR-044 required",
    "DataFlow": "preserve pre-ADR-044 required",
    "DataFlowEntityBinding": "preserve pre-ADR-044 required",
    "DataModelBinding": "preserve pre-ADR-044 required",
    "ModelSelection": "preserve pre-ADR-044 required",
    "SelectedEntity": "preserve pre-ADR-044 required",
    "SelectedAttribute": "preserve pre-ADR-044 required",
    "Metric": "preserve pre-ADR-044 required",
    "Dimension": "preserve pre-ADR-044 required",
    "SpecificationRequirement": "preserve pre-ADR-044 required",
    "DataStructure": "D1 recommended description",
    "Mapping": "D3 optional description + deprecated identity slots (2.1.0)",
}


def _schema_dir(root: Path) -> Path:
    return root / "model-assets/specifications/moex-dams/0.1/schemas"


def check_description_declarations(root: str | Path) -> list[str]:
    root = Path(root)
    schemas = _schema_dir(root)
    errors: list[str] = []
    description_defs: list[str] = []
    for path in sorted(schemas.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        slots = data.get("slots") or {}
        if "description" in slots:
            description_defs.append(path.name)
        for cname, cdef in (data.get("classes") or {}).items():
            if not isinstance(cdef, dict):
                continue
            usage = cdef.get("slot_usage") or {}
            if "description" in usage and cname not in DESCRIPTION_SLOT_USAGE_ALLOWLIST:
                errors.append(
                    f"{path.name}:{cname} has slot_usage.description "
                    f"but is not on ADR-044 allowlist"
                )
    if len(description_defs) > 1:
        errors.append(
            "description slot declared in multiple modules: "
            + ", ".join(description_defs)
            + " (must live only in moex-base.yaml)"
        )
    elif description_defs and description_defs != ["moex-base.yaml"]:
        errors.append(
            f"description slot must be declared in moex-base.yaml, found in {description_defs}"
        )
    return sorted(errors)


def check_identified_vs_embedded(root: str | Path) -> list[str]:
    from linkml_runtime.utils.schemaview import SchemaView

    schema = _schema_dir(Path(root)) / "moex-dams.yaml"
    sv = SchemaView(str(schema))
    errors: list[str] = []
    for name in ("IdentifiedElement", "EmbeddedElement"):
        if name not in sv.all_classes():
            errors.append(f"missing class {name}")
            return errors
    id_anc = set(sv.class_ancestors("IdentifiedElement", reflexive=False))
    emb_anc = set(sv.class_ancestors("EmbeddedElement", reflexive=False))
    if "IdentifiedElement" in emb_anc or "EmbeddedElement" in id_anc:
        errors.append(
            "IdentifiedElement and EmbeddedElement must not be in one is_a chain"
        )
    return errors
