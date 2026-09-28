"""Publish gate smoke (run via python -m pytest scripts/tests)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from generate_artifacts import PYTHON_MANIFEST  # noqa: E402
from publish_gate import verify_publish_gate  # noqa: E402


def test_publish_gate_passes_on_clean_checkout() -> None:
    errors = verify_publish_gate(refresh_bundle=False)
    assert errors == [], errors


def test_publish_gate_fails_on_digest_mismatch() -> None:
    orig = PYTHON_MANIFEST.read_text(encoding="utf-8")
    data = json.loads(orig)
    data["content_digest"] = "sha256:" + ("0" * 64)
    PYTHON_MANIFEST.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        errors = verify_publish_gate(refresh_bundle=False)
        assert any("python digest mismatch" in e for e in errors)
    finally:
        PYTHON_MANIFEST.write_text(orig, encoding="utf-8")
