"""Tests for scripts/migrate_mapping_labels.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load():
    path = REPO / "scripts" / "migrate_mapping_labels.py"
    spec = importlib.util.spec_from_file_location("migrate_mapping_labels", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_mapping_label_format():
    mod = _load()
    assert (
        mod.mapping_label(
            {
                "source_refs": ["a"],
                "target_refs": ["b"],
                "mapping_type": "field_mapping",
            }
        )
        == "a -> b [field_mapping]"
    )


def test_scan_finds_mappings(tmp_path: Path):
    mod = _load()
    p = tmp_path / "m.yaml"
    p.write_text(
        "mappings:\n"
        "- element_id: dams:map/1\n"
        "  name: old\n"
        "  source_refs: [dams:a]\n"
        "  target_refs: [dams:b]\n"
        "  mapping_type: realizes\n"
        "  mapping_cardinality: one_to_one\n",
        encoding="utf-8",
    )
    rows = mod.scan_file(p)
    assert len(rows) == 1
    assert rows[0]["name"] == "old"
    assert "realizes" in rows[0]["label"]
