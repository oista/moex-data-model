"""Tests for DAMS layer boundary architecture check."""

from __future__ import annotations

from pathlib import Path

from architecture_check.layer_boundaries import check_layer_boundaries

REPO = Path(__file__).resolve().parents[3]
DAMS = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"


def test_layer_boundaries_clean_on_current_schema():
    assert DAMS.is_file()
    assert check_layer_boundaries(DAMS) == []
