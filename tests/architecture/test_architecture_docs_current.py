"""Normative architecture docs must not prescribe removed DAMS shapes."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Paths that must stay current with schema on main (audit Wave B2 / R2-2).
NORMATIVE_GLOBS = (
    "docs/architecture/uml/*.puml",
    "docs/architecture/uml/description.md",
    "docs/architecture/linkml_architecture.md",
    "docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md",
    "docs/LinkML_Glossary_DAMS.md",
    "docs/dams_entities_list.md",
    "docs/MOEX Data Model Specification v0.1 на основе LinkML.md",
    "docs/IMPLEMENTATION_PLAN.md",
    "docs/agents/er-dictionary-model-contract.md",
    "docs/agents/pdf-to-er-dictionary.md",
)

# Contiguous banned tokens assembled so this file is not a false positive.
_PHYSICAL_FIELD = "Physical" + "Field"
_PHYSICAL_FIELDS = "physical" + "_fields"
_PHYSICAL_OBJECT = "Physical" + "Object"
_PHYSICAL_OBJECTS = "physical" + "_objects"
_PHYSICAL_OBJECT_REFS = "physical" + "_object_refs"
_PHYSICAL_FIELD_REFS = "physical" + "_field_refs"
_PHYSICAL_FIELD_REF = "physical" + "_field_ref"

# Removed authored DataFlow topology slots (ADR-048 PR-5). Still valid on
# TopologyView / CatalogSnapshot — allow when line mentions those read models.
_TOPOLOGY_AUTHORED = (
    "source_solution_ref",
    "target_solution_ref",
    "source_system_ref",
    "target_system_ref",
    "source_platform_ref",
    "target_platform_ref",
    "integration_level",
    "integration_class",
    "integration_channel",
    "integration_spec_ref",
)

# Removed governance target/id slots (ADR-049 PR-5).
_GOVERNANCE_LEGACY = (
    "classified_element_ref",
    "policy_target_ref",
    "policy_binding_id",
)

# Legacy ModelPackage composition edge label in PlantUML.
_MAPPINGS_EDGE = re.compile(
    r'ModelPackage\s+"1"\s+\*--\s+"0\.\.\*"\s+Mapping\s*:\s*mappings\b'
)

BANNED_PHYSICAL = (
    _PHYSICAL_FIELD,
    _PHYSICAL_FIELDS,
    _PHYSICAL_OBJECT,
    _PHYSICAL_OBJECTS,
    _PHYSICAL_OBJECT_REFS,
    _PHYSICAL_FIELD_REFS,
    _PHYSICAL_FIELD_REF,
)

_HISTORICAL_MARKERS = (
    "removed",
    "replaces",
    "вместо",
    "заменя",
    "удал",
    "legacy",
    "deprecated",
    "прежн",
    "historical",
    "историч",
)

_TOPOLOGY_READ_MODEL_MARKERS = (
    "topologyview",
    "topology_view",
    "topologyfact",
    "catalogsnapshot",
    "catalog_snapshot",
    "derived",
    "read model",
    "read-model",
)


def _iter_normative() -> list[Path]:
    files: list[Path] = []
    for pattern in NORMATIVE_GLOBS:
        files.extend(REPO.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


def _is_historical_line(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in _HISTORICAL_MARKERS)


def _is_topology_read_model_line(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in _TOPOLOGY_READ_MODEL_MARKERS)


def test_normative_architecture_docs_have_no_removed_physical_shapes() -> None:
    offenders: list[str] = []
    for path in _iter_normative():
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if _is_historical_line(line):
                continue
            for token in BANNED_PHYSICAL:
                if token in line:
                    offenders.append(f"{rel}:{i}: {line.strip()}")
                    break
    assert not offenders, (
        "Removed physical-layer class residue in normative docs:\n"
        + "\n".join(offenders[:80])
    )


def test_normative_docs_have_no_authored_topology_or_legacy_governance_slots() -> None:
    offenders: list[str] = []
    for path in _iter_normative():
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if _is_historical_line(line) or _is_topology_read_model_line(line):
                continue
            # Enum table rows like `integration_channel_enum` are not slot names.
            if "_enum" in line.lower():
                continue
            for token in _TOPOLOGY_AUTHORED + _GOVERNANCE_LEGACY:
                if token in line:
                    offenders.append(f"{rel}:{i}: {line.strip()}")
                    break
    assert not offenders, (
        "Removed DataFlow topology / governance slots in normative docs:\n"
        + "\n".join(offenders[:80])
    )


def test_uml_does_not_show_legacy_mappings_collection() -> None:
    offenders: list[str] = []
    for path in (REPO / "docs" / "architecture" / "uml").glob("*.puml"):
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            if _MAPPINGS_EDGE.search(line):
                offenders.append(f"{rel}:{i}: {line.strip()}")
    assert not offenders, (
        "UML still shows ModelPackage *-- Mapping : mappings "
        "(use typed collections):\n" + "\n".join(offenders)
    )
