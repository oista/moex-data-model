"""Normative architecture docs must not prescribe removed DAMS shapes."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Paths that must stay current with schema on main (audit Wave B2).
NORMATIVE_GLOBS = (
    "docs/architecture/uml/*.puml",
    "docs/architecture/uml/description.md",
    "docs/LinkML_Glossary_DAMS.md",
    "docs/dams_entities_list.md",
)

# Contiguous banned tokens assembled so this file is not a false positive.
_PHYSICAL_FIELD = "Physical" + "Field"
_PHYSICAL_FIELDS = "physical" + "_fields"
_PHYSICAL_OBJECT = "Physical" + "Object"
# Legacy ModelPackage composition edge label in PlantUML.
_MAPPINGS_EDGE = re.compile(
    r'ModelPackage\s+"1"\s+\*--\s+"0\.\.\*"\s+Mapping\s*:\s*mappings\b'
)

BANNED_LITERALS = (
    _PHYSICAL_FIELD,
    _PHYSICAL_FIELDS,
    _PHYSICAL_OBJECT,
)


def _iter_normative() -> list[Path]:
    files: list[Path] = []
    for pattern in NORMATIVE_GLOBS:
        files.extend(REPO.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


def test_normative_architecture_docs_have_no_removed_physical_shapes() -> None:
    offenders: list[str] = []
    for path in _iter_normative():
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            # Allow explicit "removed / replaces PhysicalField" historical notes.
            lower = line.lower()
            if any(
                marker in lower
                for marker in (
                    "removed",
                    "replaces",
                    "вместо",
                    "заменя",
                    "удал",
                    "legacy",
                )
            ):
                continue
            for token in BANNED_LITERALS:
                if token in line:
                    offenders.append(f"{rel}:{i}: {line.strip()}")
                    break
    assert not offenders, (
        "Removed PhysicalField/PhysicalObject residue in normative docs:\n"
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
