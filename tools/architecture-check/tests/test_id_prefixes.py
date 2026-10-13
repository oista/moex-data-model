"""ADR-052 id_prefixes lint."""

from __future__ import annotations

from pathlib import Path

from architecture_check.id_prefixes import (
    ID_PREFIXES_ALLOWLIST,
    ID_PREFIXES_ALLOWLIST_CEILING,
    check_id_prefixes,
    check_id_prefixes_allowlist_documented,
)

REPO = Path(__file__).resolve().parents[3]


def test_id_prefixes_clean_on_repo() -> None:
    assert check_id_prefixes(REPO) == []


def test_allowlist_documented_in_adr() -> None:
    assert check_id_prefixes_allowlist_documented(REPO) == []


def test_allowlist_ratchet_ceiling() -> None:
    # Ceiling equals current debt; lower both when a class exits (never raise
    # ID_PREFIXES_ALLOWLIST_CEILING without amending ADR-052).
    assert len(ID_PREFIXES_ALLOWLIST) == ID_PREFIXES_ALLOWLIST_CEILING
    assert ID_PREFIXES_ALLOWLIST_CEILING > 0
    assert "ModelPackage" in ID_PREFIXES_ALLOWLIST
    assert "ModelSelection" in ID_PREFIXES_ALLOWLIST
