"""Publish gate tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from moex_model_cli.bootstrap import find_repo_root
from moex_model_cli.gates.digests import artifact_paths
from moex_model_cli.gates.publish_gate import verify_publish_gate


def test_publish_gate_passes_on_clean_checkout() -> None:
    errors = verify_publish_gate(root=find_repo_root(), refresh_bundle=False)
    assert errors == [], errors


def test_publish_gate_fails_on_digest_mismatch() -> None:
    root = find_repo_root()
    paths = artifact_paths(root)
    manifest = paths["python_manifest"]
    orig = manifest.read_text(encoding="utf-8")
    data = json.loads(orig)
    data["content_digest"] = "sha256:" + ("0" * 64)
    manifest.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        errors = verify_publish_gate(root=root, refresh_bundle=False)
        assert any("python digest mismatch" in e for e in errors)
    finally:
        manifest.write_text(orig, encoding="utf-8")


def test_publish_gate_fails_on_missing_identity_field() -> None:
    root = find_repo_root()
    manifest = artifact_paths(root)["json_schema_manifest"]
    orig = manifest.read_text(encoding="utf-8")
    data = json.loads(orig)
    del data["schema_version"]
    manifest.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        errors = verify_publish_gate(root=root, refresh_bundle=False)
        assert any("missing identity field schema_version" in e for e in errors)
    finally:
        manifest.write_text(orig, encoding="utf-8")


def test_publish_gate_fails_on_schema_version_mismatch() -> None:
    root = find_repo_root()
    manifest = artifact_paths(root)["owl_manifest"]
    orig = manifest.read_text(encoding="utf-8")
    data = json.loads(orig)
    data["schema_version"] = "0.0.0-mismatch"
    manifest.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        errors = verify_publish_gate(root=root, refresh_bundle=False)
        assert any("schema_version mismatch" in e for e in errors)
    finally:
        manifest.write_text(orig, encoding="utf-8")


def test_bundle_index_digest_ignores_generated_at() -> None:
    root = find_repo_root()
    script = root / "scripts" / "build_release_bundle.py"
    spec = importlib.util.spec_from_file_location("moex_build_release_bundle", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parts = mod.collect_parts()
    d1 = mod.bundle_index_digest(parts)
    # Mutating only generated_at on the tracked index must not change digest.
    index = json.loads(mod.BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    index["generated_at"] = "1970-01-01T00:00:00+00:00"
    d2 = mod.bundle_index_digest(parts)
    assert d1 == d2
    assert d1 == index["content_digest"]


def test_release_bundle_refuses_dirty_tree(monkeypatch) -> None:
    root = find_repo_root()
    script = root / "scripts" / "build_release_bundle.py"
    spec = importlib.util.spec_from_file_location("moex_build_release_bundle_rel", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def fake_check_output(cmd, **kwargs):  # noqa: ANN001
        if cmd[:2] == ["git", "rev-parse"]:
            return "deadbeef\n"
        if cmd[:2] == ["git", "status"]:
            return " M dirty.txt\n"
        raise AssertionError(cmd)

    monkeypatch.setattr(mod.subprocess, "check_output", fake_check_output)
    try:
        mod.resolve_source_revision(release=True)
        raise AssertionError("expected RuntimeError for dirty release")
    except RuntimeError as exc:
        assert "dirty" in str(exc)


def test_refuse_generated_draft_under_imports(tmp_path: Path) -> None:
    from moex_model_cli.gates.publish_gate import refuse_generated_draft

    root = tmp_path
    job = root / "generated" / "imports" / "job-1"
    job.mkdir(parents=True)
    (job / "job.json").write_text(
        json.dumps(
            {
                "job_id": "job-1",
                "status": "generated-draft",
                "source_type": "json_schema",
                "source_path": "source.json",
                "source_digest": "sha256:0",
                "repro_command": "echo",
            }
        ),
        encoding="utf-8",
    )
    errors = refuse_generated_draft(root=root, candidate=job / "out.json")
    assert any("generated/imports" in e for e in errors)
    errors2 = refuse_generated_draft(root=root, candidate=job)
    assert any("generated-draft" in e for e in errors2)
