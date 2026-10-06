"""Fail-closed publish gate: golden artifact digests + smoke must match."""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

from moex_model_cli.bootstrap import find_repo_root
from moex_model_cli.gates.digests import (
    artifact_paths,
    directory_tree_digest,
    file_digest,
    lf_text,
    mermaid_tree_digest,
    python_artifact_digest,
    rdf_ground_digest,
)


def _check_manifest_file(
    *,
    name: str,
    manifest_path: Path,
    artifact_path: Path,
    rdf: bool = False,
    strip_volatile: bool = False,
    strip_generation_date: bool = False,
) -> list[str]:
    if not manifest_path.is_file():
        return [f"publish-gate: missing {name} manifest"]
    if not artifact_path.exists():
        return [f"publish-gate: missing {name} artifact"]
    expected = json.loads(manifest_path.read_text(encoding="utf-8")).get(
        "content_digest"
    )
    if not expected:
        return [f"publish-gate: {name} manifest missing content_digest"]
    if artifact_path.is_dir():
        if name == "mermaid":
            actual = mermaid_tree_digest(artifact_path)
        else:
            actual = directory_tree_digest(artifact_path)
    elif rdf:
        actual = rdf_ground_digest(lf_text(artifact_path), strip_volatile=strip_volatile)
    elif strip_generation_date:
        actual = python_artifact_digest(artifact_path)
    else:
        actual = file_digest(artifact_path)
    if actual != expected:
        return [
            f"publish-gate: {name} digest mismatch "
            f"(expected={expected}, actual={actual})"
        ]
    return []


def _smoke(paths: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    try:
        from rdflib import Graph

        for key in ("owl", "shacl", "rdf"):
            Graph().parse(paths[key].as_posix(), format="turtle")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"publish-gate: rdf smoke failed: {exc}")
    if b"Table " not in paths["dbml"].read_bytes():
        errors.append("publish-gate: dbml smoke missing Table")
    try:
        py_compile.compile(str(paths["python"]), doraise=True)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"publish-gate: python smoke failed: {exc}")
    index = paths["doc"] / "index.md"
    if not index.is_file() or not index.read_text(encoding="utf-8").strip():
        errors.append("publish-gate: doc smoke missing index.md")
    if paths["json_schema"].is_file() and paths["json_schema_manifest"].is_file():
        errors.extend(
            _check_manifest_file(
                name="json-schema",
                manifest_path=paths["json_schema_manifest"],
                artifact_path=paths["json_schema"],
            )
        )
    return errors


def _bundle_ok(root: Path, *, refresh_bundle: bool) -> list[str]:
    # Lazy import: scripts live at repo root; avoid sys.path pollution at import time.
    import importlib.util

    script = root / "scripts" / "build_release_bundle.py"
    if not script.is_file():
        return ["publish-gate: missing scripts/build_release_bundle.py"]
    spec = importlib.util.spec_from_file_location("moex_build_release_bundle", script)
    if spec is None or spec.loader is None:
        return ["publish-gate: cannot load build_release_bundle"]
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if refresh_bundle:
        try:
            mod.build_bundle(stage=False)
        except Exception as exc:  # noqa: BLE001
            return [f"publish-gate: bundle rebuild failed: {exc}"]

    if not mod.BUNDLE_MANIFEST.is_file():
        return ["publish-gate: missing bundle manifest"]
    bundle = json.loads(mod.BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    try:
        parts = mod.collect_parts()
    except Exception as exc:  # noqa: BLE001
        return [f"publish-gate: bundle parts incomplete: {exc}"]
    expected = bundle.get("content_digest")
    actual = mod.bundle_index_digest(parts)
    if expected != actual:
        return [
            f"publish-gate: bundle digest mismatch "
            f"(expected={expected}, actual={actual})"
        ]
    return []


def refuse_generated_draft(
    *,
    root: Path,
    candidate: Path | None = None,
) -> list[str]:
    """
    Fail closed if a path is under generated/imports or is a generated-draft job.

    Import drafts must never be published automatically (ADR-009 / Stage 7).
    """
    errors: list[str] = []
    repo = root.resolve()
    imports_root = (repo / "generated" / "imports").resolve()

    if candidate is None:
        return errors

    path = candidate if candidate.is_absolute() else (repo / candidate).resolve()
    try:
        path.relative_to(imports_root)
        errors.append(
            f"publish-gate: refusing path under generated/imports (draft-only): {path}"
        )
    except ValueError:
        pass

    # job.json with generated-draft status
    job_json = path if path.name == "job.json" else path / "job.json"
    if job_json.is_file():
        try:
            data = json.loads(job_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if data.get("status") == "generated-draft":
            errors.append(
                f"publish-gate: refusing generated-draft import job: {job_json}"
            )
    return errors


def verify_publish_gate(
    *,
    root: Path | None = None,
    refresh_bundle: bool = True,
    publish_target: Path | None = None,
) -> list[str]:
    """Return error strings; empty list means gate passed."""
    repo = (root or find_repo_root()).resolve()
    errors = refuse_generated_draft(root=repo, candidate=publish_target)
    if errors:
        return errors

    paths = artifact_paths(repo)
    checks = (
        ("owl", paths["owl_manifest"], paths["owl"], True, False, False),
        ("shacl", paths["shacl_manifest"], paths["shacl"], True, False, False),
        ("dbml", paths["dbml_manifest"], paths["dbml"], False, False, False),
        ("mermaid", paths["mermaid_manifest"], paths["mermaid"], False, False, False),
        ("python", paths["python_manifest"], paths["python"], False, False, True),
        ("rdf", paths["rdf_manifest"], paths["rdf"], True, True, False),
    )
    # doc: git keeps index_subset only — digest of on-disk tree is not compared;
    # full-tree reproducibility is enforced by compare-golden (regen → digest).
    if not paths["doc_manifest"].is_file():
        errors.append("publish-gate: missing doc manifest")
    for name, man, art, rdf, volatile, strip_date in checks:
        errors.extend(
            _check_manifest_file(
                name=name,
                manifest_path=man,
                artifact_path=art,
                rdf=rdf,
                strip_volatile=volatile,
                strip_generation_date=strip_date,
            )
        )
    if errors:
        return errors

    errors.extend(_smoke(paths))
    if errors:
        return errors

    errors.extend(_bundle_ok(repo, refresh_bundle=refresh_bundle))
    errors.extend(_binding_integrity_digests(repo))
    return errors


def _binding_integrity_digests(repo: Path) -> list[str]:
    """ADR-034: DataModelBinding.integrity_digest must match content."""
    try:
        from moex_dams.application.digest import verify_digests
    except ImportError:
        return ["publish-gate: moex_dams.application.digest unavailable"]
    _matches, mismatches = verify_digests(repo)
    return [f"publish-gate: {m.message}" for m in mismatches]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    errors = verify_publish_gate()
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"publish-gate FAILED ({len(errors)} issue(s))", file=sys.stderr)
        return 1
    print("publish-gate OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
