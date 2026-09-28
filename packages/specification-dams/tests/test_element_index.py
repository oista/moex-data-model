"""Element index shared builder."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.application.element_index import build_element_index


def test_trading_element_index_stable(trading_solution: Path) -> None:
    data = yaml.safe_load(trading_solution.read_text(encoding="utf-8"))
    entries = build_element_index(data)
    ids = {e.element_id for e in entries}
    assert "dams:model/trading/1.0.0" in ids
    assert "dams:logical/trading/Client" in ids
    kinds = {e.element_kind for e in entries}
    assert "ModelPackage" in kinds
    assert "LogicalEntity" in kinds
