"""Fail-closed publish gate: golden artifact digests + smoke must match."""

from __future__ import annotations

import hashlib
import json
import py_compile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_artifacts import (  # noqa: E402
    DBML_MANIFEST,
    DBML_PATH,
    DOC_DIR,
    DOC_MANIFEST,
    MERMAID_DIR,
    MERMAID_MANIFEST,
    OWL_MANIFEST,
    OWL_PATH,
    PYTHON_MANIFEST,
    PYTHON_PATH,
    RDF_MANIFEST,
    RDF_PATH,
    SHACL_MANIFEST,
    SHACL_PATH,
    _strip_generation_date_lines,
    directory_tree_digest,
    mermaid_tree_digest,
    rdf_ground_digest,
)
from build_release_bundle import (  # noqa: E402
    BUNDLE_MANIFEST,
    build_bundle,
    bundle_index_digest,
    collect_parts,
)


def _lf(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(_lf(path).encode("utf-8")).hexdigest()


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
        actual = rdf_ground_digest(_lf(artifact_path), strip_volatile=strip_volatile)
    elif strip_generation_date:
        actual = "sha256:" + hashlib.sha256(
            _strip_generation_date_lines(_lf(artifact_path)).encode("utf-8")
        ).hexdigest()
    else:
        actual = _file_digest(artifact_path)
    if actual != expected:
        return [
            f"publish-gate: {name} digest mismatch "
            f"(expected={expected}, actual={actual})"
        ]
    return []


def _smoke() -> list[str]:
    errors: list[str] = []
    try:
        from rdflib import Graph

        for path, label in (
            (OWL_PATH, "owl"),
            (SHACL_PATH, "shacl"),
            (RDF_PATH, "rdf"),
        ):
            Graph().parse(path.as_posix(), format="turtle")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"publish-gate: rdf smoke failed: {exc}")
    if b"Table " not in DBML_PATH.read_bytes():
        errors.append("publish-gate: dbml smoke missing Table")
    try:
        py_compile.compile(str(PYTHON_PATH), doraise=True)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"publish-gate: python smoke failed: {exc}")
    index = DOC_DIR / "index.md"
    if not index.is_file() or not index.read_text(encoding="utf-8").strip():
        errors.append("publish-gate: doc smoke missing index.md")
    return errors


def verify_publish_gate(*, refresh_bundle: bool = True) -> list[str]:
    """Return error strings; empty list means gate passed."""
    errors: list[str] = []
    errors.extend(
        _check_manifest_file(
            name="owl",
            manifest_path=OWL_MANIFEST,
            artifact_path=OWL_PATH,
            rdf=True,
        )
    )
    errors.extend(
        _check_manifest_file(
            name="shacl",
            manifest_path=SHACL_MANIFEST,
            artifact_path=SHACL_PATH,
            rdf=True,
        )
    )
    errors.extend(
        _check_manifest_file(
            name="dbml", manifest_path=DBML_MANIFEST, artifact_path=DBML_PATH
        )
    )
    errors.extend(
        _check_manifest_file(
            name="mermaid",
            manifest_path=MERMAID_MANIFEST,
            artifact_path=MERMAID_DIR,
        )
    )
    errors.extend(
        _check_manifest_file(
            name="python",
            manifest_path=PYTHON_MANIFEST,
            artifact_path=PYTHON_PATH,
            strip_generation_date=True,
        )
    )
    errors.extend(
        _check_manifest_file(
            name="doc", manifest_path=DOC_MANIFEST, artifact_path=DOC_DIR
        )
    )
    errors.extend(
        _check_manifest_file(
            name="rdf",
            manifest_path=RDF_MANIFEST,
            artifact_path=RDF_PATH,
            rdf=True,
            strip_volatile=True,
        )
    )
    if errors:
        return errors

    errors.extend(_smoke())
    if errors:
        return errors

    if refresh_bundle:
        try:
            build_bundle(stage=False)
        except Exception as exc:  # noqa: BLE001
            return [f"publish-gate: bundle rebuild failed: {exc}"]

    if not BUNDLE_MANIFEST.is_file():
        return ["publish-gate: missing bundle manifest"]
    bundle = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    try:
        parts = collect_parts()
    except Exception as exc:  # noqa: BLE001
        return [f"publish-gate: bundle parts incomplete: {exc}"]
    expected = bundle.get("content_digest")
    actual = bundle_index_digest(parts)
    if expected != actual:
        return [
            f"publish-gate: bundle digest mismatch "
            f"(expected={expected}, actual={actual})"
        ]
    return []


def main() -> int:
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
