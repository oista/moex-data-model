"""Smoke for scripts/export_owl_instances.py without optional deps."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from export_owl_instances import main  # noqa: E402


def test_export_owl_instances_exits_2_without_linkml_owl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "linkml_owl" or name.startswith("linkml_owl."):
            raise ImportError("forced missing linkml_owl")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert main([]) == 2
