"""Release registration helpers (descriptor loading)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_ontology.domain.ontology import OntologyRelease


def load_release_descriptors(directory: Path) -> list[OntologyRelease]:
    """Load ``*.yaml`` ontology release descriptors from a directory."""
    directory = directory.expanduser().resolve()
    releases: list[OntologyRelease] = []
    if not directory.is_dir():
        return releases
    for path in sorted(directory.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        releases.append(OntologyRelease.model_validate(data))
    return releases
