"""Compare regenerable golden artifacts (contracts + optional JSON Schema)."""

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


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


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

    # Regenerate into temp; compare digest only (ignore generated_at).
    sys.path.insert(0, str(REPO / "scripts"))
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
        # Also require regen matches committed bytes when digests equal expected.
        if regen_digest == expected and init_py.read_bytes() != committed.read_bytes():
            errors.append(
                "contracts regenerate digest matches but bytes differ from committed file"
            )

    return errors


def _compare_json_schema() -> list[str]:
    if not JSON_SCHEMA.is_file():
        print(f"skip json-schema golden (not present): {JSON_SCHEMA.as_posix()}")
        return []

    from linkml.generators.jsonschemagen import JsonSchemaGenerator

    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="moex-golden-jsonschema-") as tmp:
        dest = Path(tmp) / "moex-dams.schema.json"
        text = JsonSchemaGenerator(str(SCHEMA)).serialize()
        dest.write_text(text, encoding="utf-8")
        if dest.read_bytes() != JSON_SCHEMA.read_bytes():
            # Normalize line endings for cross-platform compare.
            left = dest.read_text(encoding="utf-8").replace("\r\n", "\n")
            right = JSON_SCHEMA.read_text(encoding="utf-8").replace("\r\n", "\n")
            if left != right:
                errors.append(
                    f"json-schema regenerate mismatch:\n"
                    f"  committed={JSON_SCHEMA.as_posix()}\n"
                    f"  regenerated digest={_sha256_file(dest)}\n"
                    f"  committed digest={_sha256_file(JSON_SCHEMA)}"
                )
    return errors


def main() -> int:
    errors = _compare_contracts() + _compare_json_schema()
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"compare-golden FAILED ({len(errors)} issue(s))", file=sys.stderr)
        return 1
    print("compare-golden OK (contracts" + (", json-schema" if JSON_SCHEMA.is_file() else "") + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
