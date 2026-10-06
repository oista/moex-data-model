"""Tests for DataModelBinding integrity_digest (ADR-034)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.application.digest import (
    compute_binding_digest,
    verify_digests,
    write_digests,
)


def _binding(**overrides: object) -> dict:
    base = {
        "element_id": "dams:binding/test/1",
        "name": "test",
        "model_revision": "abc",
        "selections": [{"element_id": "dams:selection/1"}],
        "integrity_digest": "sha256:deadbeef",
        "generated_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def test_compute_stable_and_ignores_generated_at() -> None:
    a = compute_binding_digest(_binding())
    b = compute_binding_digest(_binding(generated_at="2099-01-01T00:00:00Z"))
    assert a == b
    assert a.startswith("sha256:")
    assert len(a) == len("sha256:") + 64


def test_verify_match_and_mismatch(tmp_path: Path, monkeypatch) -> None:
    examples = (
        tmp_path
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
    )
    examples.mkdir(parents=True)
    good = _binding()
    good["integrity_digest"] = compute_binding_digest(good)
    path = examples / "ok.yaml"
    path.write_text(yaml.safe_dump(good, sort_keys=False), encoding="utf-8")

    matches, mismatches = verify_digests(tmp_path)
    assert len(matches) == 1 and not mismatches

    bad = _binding(integrity_digest="sha256:" + ("0" * 64))
    path.write_text(yaml.safe_dump(bad, sort_keys=False), encoding="utf-8")
    matches, mismatches = verify_digests(tmp_path)
    assert not matches and len(mismatches) == 1


def test_write_recomputes(tmp_path: Path) -> None:
    examples = (
        tmp_path
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
    )
    examples.mkdir(parents=True)
    body = _binding(integrity_digest="sha256:" + ("f" * 64))
    path = examples / "rewrite.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    written = write_digests(tmp_path)
    assert len(written) == 1
    matches, mismatches = verify_digests(tmp_path)
    assert len(matches) == 1 and not mismatches
