"""Load SSSOM-style YAML into MappingSet / SemanticBinding."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_semantic_mappings.mapping import SemanticBinding, SemanticResourceRef
from moex_semantic_mappings.mapping_set import MappingSet


def load_sssom_yaml(path: Path) -> MappingSet:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"SSSOM file must be a mapping object: {path}")
    set_id = str(data["mapping_set_id"])
    version = str(data.get("mapping_set_version", "0.0.0"))
    license_uri = data.get("license")
    bindings: list[SemanticBinding] = []
    for row in data.get("mappings") or []:
        bindings.append(_row_to_binding(row, set_id))
    return MappingSet(
        mapping_set_id=set_id,
        mapping_set_version=version,
        license=str(license_uri) if license_uri else None,
        mappings=tuple(bindings),
    )


def _row_to_binding(row: dict[str, Any], mapping_set_id: str) -> SemanticBinding:
    subject_kind = row.get("subject_kind") or _guess_kind(str(row["subject_id"]))
    object_kind = row.get("object_kind") or "ontology_entity"
    status = row.get("status") or "approved"
    return SemanticBinding(
        subject=SemanticResourceRef(
            id=str(row["subject_id"]),
            kind=subject_kind,
            label=row.get("subject_label"),
        ),
        predicate=str(row["predicate_id"]),
        object=SemanticResourceRef(
            id=str(row["object_id"]),
            kind=object_kind,
            label=row.get("object_label"),
        ),
        justification=str(row.get("mapping_justification") or "semapv:UnspecifiedMatching"),
        confidence=row.get("confidence"),
        author=row.get("author_id"),
        status=status,
        mapping_set_id=mapping_set_id,
    )


def _guess_kind(subject_id: str) -> str:
    if subject_id.startswith("dams:"):
        return "dams_element"
    if subject_id.startswith("glossary:") or subject_id.startswith("skos:"):
        return "glossary_term"
    return "linkml_class"
