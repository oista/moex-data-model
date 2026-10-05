"""Tests for merged DAMS full-spec YAML dump."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.normalizers.dams_full_spec import (
    dams_schema_root_path,
    dump_merged_dams_schema,
)
from moex_publication_viewer.publication_contract import spec_asset_dir

REPO = Path(__file__).resolve().parents[3]


def test_dump_merged_dams_schema_flattens_modules() -> None:
    spec_dir = spec_asset_dir(REPO, "moex-dams@0.1")
    assert spec_dir is not None
    schema_path = dams_schema_root_path(spec_dir)
    text = dump_merged_dams_schema(schema_path)
    assert text.startswith("# Generated:")
    assert "schemas/" in text.splitlines()[1]
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    imports = data.get("imports") or []
    assert imports == []
    classes = data.get("classes") or {}
    assert "ConceptualEntity" in classes
    assert "LogicalEntity" in classes
    assert "DataCarrier" in classes
    assert ("Physical" + "Object") not in classes
    # Non-core modules must be inlined too.
    assert "DataFlow" in classes or "RegistryEntry" in classes
    assert "SpecificationRequirement" in classes
