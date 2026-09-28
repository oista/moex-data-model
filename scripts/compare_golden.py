"""Compare regenerable golden artifacts (contracts + JSON Schema + Stage 6 matrix)."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "generated" / "manifests" / "moex-dams-contracts.json"
JSON_SCHEMA = (
    REPO / "generated" / "artifacts" / "moex-dams" / "0.1" / "moex-dams.schema.json"
)
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)

sys.path.insert(0, str(REPO / "scripts"))
from generate_artifacts import (  # noqa: E402
    DBML_MANIFEST,
    DBML_PATH,
    DOC_DIR,
    DOC_MANIFEST,
    JSON_SCHEMA_MANIFEST,
    JSON_SCHEMA_PATH,
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
    generate_dbml,
    generate_doc,
    generate_json_schema,
    generate_mermaid,
    generate_owl,
    generate_python,
    generate_rdf,
    generate_shacl,
    mermaid_tree_digest,
    rdf_ground_digest,
    strip_generation_date_lines,
)

JSON_SCHEMA = JSON_SCHEMA_PATH


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _lf_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def _compare_contracts() -> list[str]:
    errors: list[str] = []
    if not MANIFEST.is_file():
        return [f"missing manifest: {MANIFEST}"]

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    output_rel = manifest.get("output_path")
    expected = manifest.get("content_digest")
    if not output_rel or not expected:
        return ["manifest missing output_path or content_digest"]

    committed = REPO / output_rel
    if not committed.is_file():
        return [f"missing committed artifact: {committed}"]

    actual = _sha256_file(committed)
    if actual != expected:
        errors.append(
            f"contracts digest mismatch vs manifest:\n"
            f"  file={committed.as_posix()}\n"
            f"  expected={expected}\n"
            f"  actual={actual}"
        )

    from generate_contracts import generate  # noqa: WPS433

    with tempfile.TemporaryDirectory(prefix="moex-golden-contracts-") as tmp:
        tmp_path = Path(tmp)
        out_root = tmp_path / "contracts"
        tmp_manifest = tmp_path / "manifest.json"
        init_py, regen_digest = generate(out_root=out_root, manifest_path=tmp_manifest)
        if regen_digest != expected:
            errors.append(
                f"contracts regenerate digest mismatch:\n"
                f"  expected={expected}\n"
                f"  regenerated={regen_digest}\n"
                f"  temp={init_py}"
            )
        if regen_digest == expected and init_py.read_bytes() != committed.read_bytes():
            errors.append(
                "contracts regenerate digest matches but bytes differ from committed file"
            )

    return errors


def _compare_json_schema() -> list[str]:
    if not JSON_SCHEMA_MANIFEST.is_file() and not JSON_SCHEMA.is_file():
        print(f"skip json-schema golden (not present): {JSON_SCHEMA.as_posix()}")
        return []
    return _compare_single_file(
        name="json-schema",
        manifest_path=JSON_SCHEMA_MANIFEST,
        committed_path=JSON_SCHEMA,
        regenerate=generate_json_schema,
    )


def _compare_single_file(
    *,
    name: str,
    manifest_path: Path,
    committed_path: Path,
    regenerate,
    rdf: bool = False,
    strip_volatile: bool = False,
    strip_generation_date: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not manifest_path.is_file():
        return [f"missing {name} manifest: {manifest_path}"]
    if not committed_path.is_file():
        return [f"missing committed {name} artifact: {committed_path}"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("content_digest")
    if not expected:
        return [f"{name} manifest missing content_digest"]

    committed_text = _lf_text(committed_path)
    if rdf:
        committed_digest = rdf_ground_digest(
            committed_text, strip_volatile=strip_volatile
        )
    elif strip_generation_date:
        committed_digest = "sha256:" + hashlib.sha256(
            strip_generation_date_lines(committed_text).encode("utf-8")
        ).hexdigest()
    else:
        committed_digest = "sha256:" + hashlib.sha256(
            committed_text.encode("utf-8")
        ).hexdigest()
    if committed_digest != expected:
        errors.append(
            f"{name} digest mismatch vs manifest:\n"
            f"  file={committed_path.as_posix()}\n"
            f"  expected={expected}\n"
            f"  actual={committed_digest}"
        )

    with tempfile.TemporaryDirectory(prefix=f"moex-golden-{name}-") as tmp:
        tmp_path = Path(tmp)
        out = tmp_path / committed_path.name
        tmp_manifest = tmp_path / "manifest.json"
        regen_digest = regenerate(out_path=out, manifest_path=tmp_manifest)
        if regen_digest != expected:
            errors.append(
                f"{name} regenerate digest mismatch:\n"
                f"  expected={expected}\n"
                f"  regenerated={regen_digest}"
            )
        elif not rdf and not strip_generation_date:
            left = _lf_text(out)
            if left != committed_text:
                errors.append(
                    f"{name} regenerate digest matches but text differs from committed"
                )

    return errors


def _smoke_rdf(path: Path, *, name: str) -> list[str]:
    try:
        from rdflib import Graph

        Graph().parse(path.as_posix(), format="turtle")
    except Exception as exc:  # noqa: BLE001 — surface parse failures to CI
        return [f"{name} rdflib parse failed: {exc}"]
    return []


def _smoke_dbml(path: Path) -> list[str]:
    data = path.read_bytes()
    if b"Table " not in data:
        return [f"dbml smoke: missing 'Table ' in {path.as_posix()}"]
    return []


def _smoke_mermaid(directory: Path) -> list[str]:
    errors: list[str] = []
    files = sorted(directory.glob("*.md"))
    if not files:
        return [f"mermaid smoke: no *.md under {directory.as_posix()}"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "```mermaid" not in text and "```{mermaid}" not in text:
            errors.append(f"mermaid smoke: no mermaid fence in {path.name}")
    return errors


def _compare_owl() -> list[str]:
    errors = _compare_single_file(
        name="owl",
        manifest_path=OWL_MANIFEST,
        committed_path=OWL_PATH,
        regenerate=generate_owl,
        rdf=True,
    )
    if not errors:
        errors.extend(_smoke_rdf(OWL_PATH, name="owl"))
    return errors


def _compare_shacl() -> list[str]:
    errors = _compare_single_file(
        name="shacl",
        manifest_path=SHACL_MANIFEST,
        committed_path=SHACL_PATH,
        regenerate=generate_shacl,
        rdf=True,
    )
    if not errors:
        errors.extend(_smoke_rdf(SHACL_PATH, name="shacl"))
    return errors


def _compare_dbml() -> list[str]:
    errors = _compare_single_file(
        name="dbml",
        manifest_path=DBML_MANIFEST,
        committed_path=DBML_PATH,
        regenerate=generate_dbml,
    )
    if not errors:
        errors.extend(_smoke_dbml(DBML_PATH))
    return errors


def _compare_mermaid() -> list[str]:
    errors: list[str] = []
    if not MERMAID_MANIFEST.is_file():
        return [f"missing mermaid manifest: {MERMAID_MANIFEST}"]
    if not MERMAID_DIR.is_dir():
        return [f"missing mermaid directory: {MERMAID_DIR}"]

    manifest = json.loads(MERMAID_MANIFEST.read_text(encoding="utf-8"))
    expected = manifest.get("content_digest")
    if not expected:
        return ["mermaid manifest missing content_digest"]

    actual = mermaid_tree_digest(MERMAID_DIR)
    if actual != expected:
        errors.append(
            f"mermaid digest mismatch vs manifest:\n"
            f"  dir={MERMAID_DIR.as_posix()}\n"
            f"  expected={expected}\n"
            f"  actual={actual}"
        )

    with tempfile.TemporaryDirectory(prefix="moex-golden-mermaid-") as tmp:
        tmp_dir = Path(tmp) / "diagrams"
        tmp_manifest = Path(tmp) / "manifest.json"
        regen_digest = generate_mermaid(out_dir=tmp_dir, manifest_path=tmp_manifest)
        if regen_digest != expected:
            errors.append(
                f"mermaid regenerate digest mismatch:\n"
                f"  expected={expected}\n"
                f"  regenerated={regen_digest}"
            )

    if not errors:
        errors.extend(_smoke_mermaid(MERMAID_DIR))
    return errors


def _smoke_python(path: Path) -> list[str]:
    import py_compile

    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:  # noqa: BLE001
        return [f"python smoke: compile failed: {exc}"]
    return []


def _smoke_doc(directory: Path) -> list[str]:
    import re

    if not directory.is_dir():
        return [f"doc smoke: missing directory {directory.as_posix()}"]
    files = [p for p in directory.rglob("*.md") if p.name != "README.md"]
    if not files:
        return [f"doc smoke: no *.md under {directory.as_posix()}"]
    index = directory / "index.md"
    if not index.is_file() or not index.read_text(encoding="utf-8").strip():
        return ["doc smoke: missing or empty index.md"]
    body = index.read_text(encoding="utf-8")
    match = re.search(r"\]\(([^)\s#]+\.md)\)", body)
    if match:
        linked = match.group(1)
        if not (directory / linked).is_file():
            return [f"doc smoke: index links to missing {linked}"]
    return []


def _compare_python() -> list[str]:
    errors = _compare_single_file(
        name="python",
        manifest_path=PYTHON_MANIFEST,
        committed_path=PYTHON_PATH,
        regenerate=generate_python,
        strip_generation_date=True,
    )
    if not errors:
        errors.extend(_smoke_python(PYTHON_PATH))
    return errors


def _compare_doc() -> list[str]:
    """Doc golden is regen-to-digest only (git keeps index_subset, not full tree)."""
    errors: list[str] = []
    if not DOC_MANIFEST.is_file():
        return [f"missing doc manifest: {DOC_MANIFEST}"]
    # Committed checkout may only have index.md + README.md (git_policy index_subset).
    index = DOC_DIR / "index.md"
    if not index.is_file() or not index.read_text(encoding="utf-8").strip():
        return ["doc smoke: missing or empty committed index.md"]

    manifest = json.loads(DOC_MANIFEST.read_text(encoding="utf-8"))
    expected = manifest.get("content_digest")
    if not expected:
        return ["doc manifest missing content_digest"]

    with tempfile.TemporaryDirectory(prefix="moex-golden-doc-") as tmp:
        tmp_dir = Path(tmp) / "docs"
        tmp_manifest = Path(tmp) / "manifest.json"
        regen_digest = generate_doc(out_dir=tmp_dir, manifest_path=tmp_manifest)
        if regen_digest != expected:
            errors.append(
                f"doc regenerate digest mismatch:\n"
                f"  expected={expected}\n"
                f"  regenerated={regen_digest}"
            )
        if not errors:
            errors.extend(_smoke_doc(tmp_dir))
    return errors


def _compare_rdf() -> list[str]:
    errors = _compare_single_file(
        name="rdf",
        manifest_path=RDF_MANIFEST,
        committed_path=RDF_PATH,
        regenerate=generate_rdf,
        rdf=True,
        strip_volatile=True,
    )
    if not errors:
        errors.extend(_smoke_rdf(RDF_PATH, name="rdf"))
    return errors


def _compare_bundle() -> list[str]:
    from build_release_bundle import (
        BUNDLE_MANIFEST,
        bundle_index_digest,
        collect_parts,
    )

    if not BUNDLE_MANIFEST.is_file():
        return [f"missing bundle manifest: {BUNDLE_MANIFEST.as_posix()}"]
    try:
        parts = collect_parts()
    except FileNotFoundError as exc:
        return [f"bundle: {exc}"]

    actual = bundle_index_digest(parts)
    manifest = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))
    expected = manifest.get("content_digest")
    if not expected:
        return ["bundle manifest missing content_digest"]
    if actual != expected:
        return [
            "bundle digest mismatch vs manifest:\n"
            f"  expected={expected}\n"
            f"  actual={actual}\n"
            "  hint: run python scripts/build_release_bundle.py"
        ]
    return []


def main() -> int:
    parts = ["contracts"]
    errors = _compare_contracts() + _compare_json_schema()
    if JSON_SCHEMA.is_file():
        parts.append("json-schema")

    for name, fn in (
        ("owl", _compare_owl),
        ("shacl", _compare_shacl),
        ("dbml", _compare_dbml),
        ("mermaid", _compare_mermaid),
        ("python", _compare_python),
        ("doc", _compare_doc),
        ("rdf", _compare_rdf),
    ):
        chunk = fn()
        errors.extend(chunk)
        if not chunk or all("missing" not in e for e in chunk):
            # Always list target once present in repo after Stage 6 baseline.
            if (REPO / "generated" / "manifests" / f"moex-dams-{name}.json").is_file():
                parts.append(name)

    bundle_errors = _compare_bundle()
    errors.extend(bundle_errors)
    if not bundle_errors and (
        REPO / "generated" / "manifests" / "moex-dams-bundle.json"
    ).is_file():
        parts.append("bundle")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"compare-golden FAILED ({len(errors)} issue(s))", file=sys.stderr)
        return 1
    print("compare-golden OK (" + ", ".join(parts) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
