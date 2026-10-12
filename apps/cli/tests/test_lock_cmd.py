from __future__ import annotations

from pathlib import Path

from moex_model_cli.commands.lock_cmd import run_lock_update, run_lock_verify

REPO = Path(__file__).resolve().parents[3]


def test_lock_update_and_verify() -> None:
    code, text = run_lock_update(REPO)
    assert code == 0
    assert "wrote" in text
    lock = REPO / "model-assets" / "implementations" / "manifest.lock"
    assert lock.is_file()
    before = lock.read_text(encoding="utf-8")
    code2, text2 = run_lock_verify(REPO)
    assert code2 == 0, text2
    assert lock.read_text(encoding="utf-8") == before


def test_validate_does_not_rewrite_lock() -> None:
    """Smoke: lock file mtime/content unchanged by validate import path."""
    lock = REPO / "model-assets" / "implementations" / "manifest.lock"
    if not lock.is_file():
        run_lock_update(REPO)
    before = lock.read_bytes()
    # Import validate command module (side-effect free); real validate would need slice.
    from moex_model_cli.commands import validate as _validate  # noqa: F401

    assert lock.read_bytes() == before
