"""Publish gate tests."""

from __future__ import annotations

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
