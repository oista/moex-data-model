"""Generate regenerable DAMS LinkML artifacts: OWL, SHACL, DBML, Mermaid."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Iterator, Sequence

REPO = Path(__file__).resolve().parents[1]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
ARTIFACTS_ROOT = REPO / "generated" / "artifacts" / "moex-dams" / "0.1"
MANIFESTS = REPO / "generated" / "manifests"

OWL_PATH = ARTIFACTS_ROOT / "moex-dams.owl.ttl"
SHACL_PATH = ARTIFACTS_ROOT / "moex-dams.shacl.ttl"
DBML_PATH = ARTIFACTS_ROOT / "moex-dams.dbml"
MERMAID_DIR = ARTIFACTS_ROOT / "diagrams"

OWL_MANIFEST = MANIFESTS / "moex-dams-owl.json"
SHACL_MANIFEST = MANIFESTS / "moex-dams-shacl.json"
DBML_MANIFEST = MANIFESTS / "moex-dams-dbml.json"
MERMAID_MANIFEST = MANIFESTS / "moex-dams-mermaid.json"

OWL_OPTIONS = {
    "format": "ttl",
    "skip_vacuous_min_zero_cardinality_axioms": True,
    "skip_vacuous_local_range_axioms": True,
    "consolidate_cardinality_axioms": True,
}

ALL_TARGETS = ("owl", "shacl", "dbml", "mermaid")


def _linkml_version() -> str:
    try:
        return version("linkml")
    except PackageNotFoundError:
        return "unknown"


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


def schema_digest() -> str:
    return _sha256_bytes(SCHEMA.read_bytes())


def schema_rel() -> str:
    return SCHEMA.relative_to(REPO).as_posix()


@contextmanager
def schema_cwd() -> Iterator[str]:
    """LinkML imports resolve relative to the schema directory."""
    prev = Path.cwd()
    os.chdir(SCHEMA.parent)
    try:
        yield SCHEMA.name
    finally:
        os.chdir(prev)


def write_text_artifact(path: Path, text: str) -> str:
    """Write UTF-8 text with LF newlines; return content digest."""
    normalized = text.replace("\r\n", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return _sha256_text(normalized)


def mermaid_tree_digest(directory: Path) -> str:
    """Stable digest over sorted relative path + content for all *.md files."""
    h = hashlib.sha256()
    files = sorted(directory.glob("*.md"), key=lambda p: p.name.lower())
    for path in files:
        rel = path.name
        body = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(body.encode("utf-8"))
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def write_manifest(
    *,
    path: Path,
    artifact_id: str,
    generator: str,
    generator_module: str,
    output_path: str,
    content_digest: str,
    generator_options: dict | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest: dict = {
        "artifact_id": artifact_id,
        "generator": generator,
        "generator_module": generator_module,
        "generator_version": _linkml_version(),
        "schema_path": schema_rel(),
        "schema_digest": schema_digest(),
        "output_path": output_path,
        "content_digest": content_digest,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if generator_options is not None:
        manifest["generator_options"] = generator_options
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def generate_owl(*, out_path: Path = OWL_PATH, manifest_path: Path = OWL_MANIFEST) -> str:
    from linkml.generators.owlgen import OwlSchemaGenerator

    with schema_cwd() as schema_name:
        gen = OwlSchemaGenerator(schema_name, **OWL_OPTIONS)
        text = gen.serialize()
    digest = write_text_artifact(out_path, text)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-owl:0.1",
        generator="gen-owl",
        generator_module="linkml.generators.owlgen",
        output_path=out_rel,
        content_digest=digest,
        generator_options=dict(OWL_OPTIONS),
    )
    return digest


def generate_shacl(
    *, out_path: Path = SHACL_PATH, manifest_path: Path = SHACL_MANIFEST
) -> str:
    from linkml.generators.shaclgen import ShaclGenerator

    with schema_cwd() as schema_name:
        gen = ShaclGenerator(schema_name)
        text = gen.serialize()
    digest = write_text_artifact(out_path, text)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-shacl:0.1",
        generator="gen-shacl",
        generator_module="linkml.generators.shaclgen",
        output_path=out_rel,
        content_digest=digest,
    )
    return digest


def generate_dbml(
    *, out_path: Path = DBML_PATH, manifest_path: Path = DBML_MANIFEST
) -> str:
    from linkml.generators.dbmlgen import DBMLGenerator

    with schema_cwd() as schema_name:
        gen = DBMLGenerator(schema_name)
        text = gen.serialize()
    digest = write_text_artifact(out_path, text)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-dbml:0.1",
        generator="gen-dbml",
        generator_module="linkml.generators.dbmlgen",
        output_path=out_rel,
        content_digest=digest,
    )
    return digest


def generate_mermaid(
    *, out_dir: Path = MERMAID_DIR, manifest_path: Path = MERMAID_MANIFEST
) -> str:
    from linkml.generators.mermaidclassdiagramgen import MermaidClassDiagramGenerator

    out_dir.mkdir(parents=True, exist_ok=True)
    # Remove stale class diagrams so removed classes do not linger.
    for old in out_dir.glob("*.md"):
        old.unlink()

    with schema_cwd() as schema_name:
        gen = MermaidClassDiagramGenerator(schema_name, directory=str(out_dir))
        gen.generate_class_diagrams()

    # Normalize newlines in place.
    for path in out_dir.glob("*.md"):
        body = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if not body.endswith("\n"):
            body += "\n"
        path.write_text(body, encoding="utf-8", newline="\n")

    digest = mermaid_tree_digest(out_dir)
    try:
        out_rel = out_dir.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_dir.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-mermaid:0.1",
        generator="gen-mermaid-class-diagram",
        generator_module="linkml.generators.mermaidclassdiagramgen",
        output_path=out_rel,
        content_digest=digest,
    )
    return digest


def generate(targets: Sequence[str] = ALL_TARGETS) -> dict[str, str]:
    if not SCHEMA.is_file():
        raise FileNotFoundError(f"missing schema: {SCHEMA}")
    digests: dict[str, str] = {}
    for target in targets:
        if target == "owl":
            digests["owl"] = generate_owl()
        elif target == "shacl":
            digests["shacl"] = generate_shacl()
        elif target == "dbml":
            digests["dbml"] = generate_dbml()
        elif target == "mermaid":
            digests["mermaid"] = generate_mermaid()
        else:
            raise ValueError(f"unknown target: {target}")
    return digests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        action="append",
        choices=ALL_TARGETS,
        dest="only",
        help="Generate only this target (repeatable; default: all)",
    )
    args = parser.parse_args(argv)
    targets = tuple(args.only) if args.only else ALL_TARGETS

    try:
        digests = generate(targets)
    except Exception as exc:
        print(f"generate_artifacts failed: {exc}", file=sys.stderr)
        return 1

    for name, digest in digests.items():
        print(f"{name}: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
