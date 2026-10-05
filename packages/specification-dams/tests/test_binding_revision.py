"""Unit tests for DataModelBinding integrity_digest / revision policy."""

from __future__ import annotations

from moex_dams.application.binding_revision import (
    apply_binding_revision_policy,
    compute_integrity_digest,
)


def _binding(**overrides):
    base = {
        "element_id": "dams:binding/demo/1.0.0",
        "model_package_ref": "https://example/models/x/0.1.0",
        "model_version": "0.1.0",
        "model_revision": "abc123",
        "selections": [{"element_id": "dams:selection/x"}],
        "compatibility_mode": "backward",
        "integrity_digest": "sha256:" + ("0" * 64),
    }
    base.update(overrides)
    return base


def test_demo_recomputes_digest_in_place():
    b = _binding()
    old_rev = b["model_revision"]
    data = {"data_model_bindings": [b]}
    lines = apply_binding_revision_policy(data, demo=True)
    assert any("RECOMPUTED" in line for line in lines)
    assert b["model_revision"] == old_rev
    assert "compatibility_baseline_ref" not in b
    assert b["integrity_digest"] == compute_integrity_digest(b)
    assert b["integrity_digest"].startswith("sha256:")


def test_production_issues_new_revision_with_baseline():
    b = _binding()
    old_rev = b["model_revision"]
    old_digest = b["integrity_digest"]
    data = {"data_model_bindings": [b]}
    lines = apply_binding_revision_policy(
        data, demo=False, reason="attribute-semantics-migration"
    )
    assert any("NEW_REVISION" in line for line in lines)
    assert b["model_revision"] != old_rev
    assert b["compatibility_baseline_ref"] == (
        f"dams:binding/demo/1.0.0/rev/{old_rev}"
    )
    assert b["integrity_digest"] != old_digest
    assert b["integrity_digest"] == compute_integrity_digest(b)


def test_standalone_binding_document():
    b = _binding()
    apply_binding_revision_policy(b, demo=True)
    assert b["integrity_digest"] == compute_integrity_digest(b)


def test_no_bindings_noop():
    data = {"logical_entities": []}
    assert apply_binding_revision_policy(data, demo=False) == []
