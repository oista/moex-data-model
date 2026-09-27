"""SKOS concept scheme projection for business glossary terms."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict


class GlossaryConcept(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    id: str
    pref_label: str
    definition: str | None = None
    alt_labels: tuple[str, ...] = ()
    broader: tuple[str, ...] = ()
    narrower: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    mappings: tuple[str, ...] = ()


def load_skos_concept_scheme(path: Path) -> list[GlossaryConcept]:
    """Load a small YAML concept scheme (not OWL classes)."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    concepts_raw = data.get("concepts") if isinstance(data, dict) else data
    if not isinstance(concepts_raw, list):
        raise ValueError(f"Expected concepts list in {path}")
    concepts: list[GlossaryConcept] = []
    for row in concepts_raw:
        concepts.append(
            GlossaryConcept(
                id=str(row["id"]),
                pref_label=str(row["prefLabel"]),
                definition=row.get("definition"),
                alt_labels=tuple(row.get("altLabel") or []),
                broader=tuple(row.get("broader") or []),
                narrower=tuple(row.get("narrower") or []),
                related=tuple(row.get("related") or []),
                mappings=tuple(row.get("mappings") or []),
            )
        )
    return concepts
