"""ADR-052 id_prefixes lint."""

from __future__ import annotations

from pathlib import Path

from architecture_check.id_prefixes import ID_PREFIXES_ALLOWLIST, check_id_prefixes

REPO = Path(__file__).resolve().parents[3]


def test_id_prefixes_clean_on_repo() -> None:
    assert check_id_prefixes(REPO) == []


def test_allowlist_non_empty_snapshot() -> None:
    # Guard against accidental empty allowlist wiping the gate.
    assert len(ID_PREFIXES_ALLOWLIST) >= 20
    assert "ModelPackage" in ID_PREFIXES_ALLOWLIST
