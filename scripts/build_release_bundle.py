"""Build DAMS 0.1 release bundle index + staged directory of golden artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFESTS = REPO / "generated" / "manifests"
BUNDLE_DIR = REPO / "generated" / "bundles" / "moex-dams" / "0.1"
BUNDLE_MANIFEST = MANIFESTS / "moex-dams-bundle.json"
REQUIREMENTS = REPO / "requirements-linkml.txt"
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)


def schema_version() -> str:
    for line in SCHEMA.read_text(encoding="utf-8").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise ValueError(f"missing version: in {SCHEMA}")


def resolve_source_revision(*, release: bool = False) -> str:
    """Git SHA for staged bundle only (ADR-052 D7). Tracked manifests omit this."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        if release:
            raise RuntimeError(
                "release bundle requires git revision; git unavailable"
            ) from None
        return "unknown"
    if dirty:
        if release:
            raise RuntimeError(
                "release bundle refuses dirty working tree "
                "(commit or stash before --release)"
            )
        return "unknown"
    return sha

# (path relative to repo, role, optional artifact-manifest for stable digest)
BUNDLE_PARTS: tuple[tuple[str, str, str | None], ...] = (
    (
        "generated/contracts/moex-dams/0.1",
        "contracts",
        "generated/manifests/moex-dams-contracts.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/moex-dams.schema.json",
        "json-schema",
        "generated/manifests/moex-dams-json-schema.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/moex-dams.owl.ttl",
        "owl",
        "generated/manifests/moex-dams-owl.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/moex-dams.shacl.ttl",
        "shacl",
        "generated/manifests/moex-dams-shacl.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/moex-dams.dbml",
        "dbml",
        "generated/manifests/moex-dams-dbml.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/diagrams",
        "mermaid",
        "generated/manifests/moex-dams-mermaid.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/python/moex_dams.py",
        "python",
        "generated/manifests/moex-dams-python.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/docs",
        "doc",
        "generated/manifests/moex-dams-doc.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/moex-dams.rdf.ttl",
        "rdf",
        "generated/manifests/moex-dams-rdf.json",
    ),
    (
        "generated/artifacts/moex-dams/0.1/ontology-profile.json",
        "ontology-profile",
        "generated/manifests/moex-dams-ontology-profile.json",
    ),
    ("requirements-linkml.txt", "toolchain", None),
)


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    if path.is_file():
        return _sha256_bytes(path.read_bytes())
    h = hashlib.sha256()
    children = [
        p
        for p in path.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")
    ]
    for child in sorted(children, key=lambda p: p.relative_to(path).as_posix().lower()):
        rel = child.relative_to(path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(child.read_bytes())
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def _part_digest(path: Path, manifest_rel: str | None) -> str:
    """Prefer stable content_digest from artifact manifest when present."""
    if manifest_rel:
        manifest_path = REPO / manifest_rel
        if not manifest_path.is_file():
            raise FileNotFoundError(f"bundle part manifest missing: {manifest_rel}")
        digest = json.loads(manifest_path.read_text(encoding="utf-8")).get(
            "content_digest"
        )
        if not digest:
            raise ValueError(f"bundle part manifest missing content_digest: {manifest_rel}")
        return str(digest)
    return _sha256_path(path)


def collect_parts() -> list[dict]:
    parts: list[dict] = []
    for rel, role, manifest_rel in BUNDLE_PARTS:
        path = REPO / rel
        if not path.exists():
            raise FileNotFoundError(f"bundle part missing: {rel}")
        entry: dict = {
            "path": rel,
            "role": role,
            "content_digest": _part_digest(path, manifest_rel),
        }
        if manifest_rel:
            entry["manifest_path"] = manifest_rel
        parts.append(entry)
    return parts


def bundle_index_digest(parts: list[dict]) -> str:
    # Digest only role+content_digest (stable); ignore generated_at noise.
    slim = [{"role": p["role"], "content_digest": p["content_digest"]} for p in parts]
    payload = json.dumps(slim, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def stage_bundle(parts: list[dict], staged_index: dict) -> None:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    for part in parts:
        src = REPO / part["path"]
        dest = BUNDLE_DIR / part["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(
                src,
                dest,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(src, dest)
    (BUNDLE_DIR / "BUNDLE.json").write_text(
        json.dumps(staged_index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_bundle(*, stage: bool = True, release: bool = False) -> dict:
    parts = collect_parts()
    content_digest = bundle_index_digest(parts)
    toolchain_digest = _sha256_path(REQUIREMENTS)
    version = schema_version()
    source_revision = resolve_source_revision(release=release)
    if BUNDLE_MANIFEST.is_file():
        try:
            existing = json.loads(BUNDLE_MANIFEST.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        existing_parts = existing.get("parts") or []
        same_parts = [
            {"role": p.get("role"), "content_digest": p.get("content_digest")}
            for p in existing_parts
        ]
        new_parts = [
            {"role": p["role"], "content_digest": p["content_digest"]} for p in parts
        ]
        if (
            existing.get("content_digest") == content_digest
            and existing.get("toolchain_digest") == toolchain_digest
            and existing.get("schema_version") == version
            and existing.get("role") == "bundle"
            and existing.get("media_type") == "application/json"
            and same_parts == new_parts
        ):
            # Never persist source_revision on the tracked index (ADR-052 D7).
            tracked = {
                k: v for k, v in existing.items() if k != "source_revision"
            }
            if stage:
                staged = {**tracked, "source_revision": source_revision}
                if not BUNDLE_DIR.exists():
                    stage_bundle(parts, staged)
                else:
                    (BUNDLE_DIR / "BUNDLE.json").write_text(
                        json.dumps(staged, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
            return tracked

    index = {
        "artifact_id": "moex:artifact:dams-bundle:0.1",
        "schema_path": (
            "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
        ),
        "schema_version": version,
        "role": "bundle",
        "media_type": "application/json",
        "toolchain_pin": "requirements-linkml.txt",
        "toolchain_digest": toolchain_digest,
        "bundle_dir": BUNDLE_DIR.relative_to(REPO).as_posix(),
        "parts": parts,
        "content_digest": content_digest,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    BUNDLE_MANIFEST.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if stage:
        staged = {**index, "source_revision": source_revision}
        stage_bundle(parts, staged)
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-stage",
        action="store_true",
        help="Only write moex-dams-bundle.json (no copy tree)",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Require clean git tree; embed source_revision in staged BUNDLE.json",
    )
    args = parser.parse_args(argv)
    try:
        index = build_bundle(stage=not args.no_stage, release=args.release)
    except Exception as exc:  # noqa: BLE001
        print(f"build_release_bundle failed: {exc}", file=sys.stderr)
        return 1
    print(f"bundle: {index['content_digest']} parts={len(index['parts'])}")
    print(f"manifest: {BUNDLE_MANIFEST.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
