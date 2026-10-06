"""Generate regenerable DAMS LinkML artifacts: OWL, SHACL, DBML, Mermaid, Python, Doc, RDF."""

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
PYTHON_DIR = ARTIFACTS_ROOT / "python"
PYTHON_PATH = PYTHON_DIR / "moex_dams.py"
DOC_DIR = ARTIFACTS_ROOT / "docs"
RDF_PATH = ARTIFACTS_ROOT / "moex-dams.rdf.ttl"
JSON_SCHEMA_PATH = ARTIFACTS_ROOT / "moex-dams.schema.json"
ONTOLOGY_PROFILE_PATH = ARTIFACTS_ROOT / "ontology-profile.json"
ONTOLOGY_PROFILE_MD_PATH = ARTIFACTS_ROOT / "ontology-profile.md"

OWL_MANIFEST = MANIFESTS / "moex-dams-owl.json"
SHACL_MANIFEST = MANIFESTS / "moex-dams-shacl.json"
DBML_MANIFEST = MANIFESTS / "moex-dams-dbml.json"
MERMAID_MANIFEST = MANIFESTS / "moex-dams-mermaid.json"
PYTHON_MANIFEST = MANIFESTS / "moex-dams-python.json"
DOC_MANIFEST = MANIFESTS / "moex-dams-doc.json"
RDF_MANIFEST = MANIFESTS / "moex-dams-rdf.json"
JSON_SCHEMA_MANIFEST = MANIFESTS / "moex-dams-json-schema.json"
ONTOLOGY_PROFILE_MANIFEST = MANIFESTS / "moex-dams-ontology-profile.json"

OWL_OPTIONS = {
    "format": "ttl",
    "skip_vacuous_min_zero_cardinality_axioms": True,
    "skip_vacuous_local_range_axioms": True,
    "consolidate_cardinality_axioms": True,
}

ALL_TARGETS = (
    "owl",
    "shacl",
    "dbml",
    "mermaid",
    "python",
    "doc",
    "rdf",
    "json-schema",
    "ontology-report",
)

try:
    from moex_model_cli.gates.digests import (  # type: ignore
        VOLATILE_RDF_PREDICATES as _VOLATILE_RDF_PREDICATES,
        strip_generation_date_lines,
    )
except ImportError:  # scripts/ generate without editable CLI install

    def strip_generation_date_lines(text: str) -> str:
        lines = [
            line
            for line in text.split("\n")
            if not line.startswith("# Generation date:")
        ]
        return "\n".join(lines)

    _VOLATILE_RDF_PREDICATES = frozenset(
        {
            "https://w3id.org/linkml/generation_date",
            "http://www.w3.org/ns/prov#generatedAtTime",
        }
    )

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
    return _sha256_bytes(SCHEMA.read_bytes().replace(b"\r\n", b"\n"))


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


def write_text_artifact(
    path: Path, text: str, *, strip_generation_date: bool = False
) -> str:
    """Write UTF-8 text with LF newlines; return content digest."""
    normalized = text.replace("\r\n", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    digest_source = (
        strip_generation_date_lines(normalized)
        if strip_generation_date
        else normalized
    )
    digest = _sha256_text(digest_source)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and strip_generation_date:
        existing = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if _sha256_text(strip_generation_date_lines(existing)) == digest:
            return digest
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return digest

def rdf_ground_digest(text: str, *, strip_volatile: bool = False) -> str:
    """Stable digest of non-blank-node triples (LinkML OWL/SHACL order varies)."""
    from rdflib import BNode, Graph

    graph = Graph()
    graph.parse(data=text, format="turtle")
    lines: list[str] = []
    for subj, pred, obj in graph:
        if isinstance(subj, BNode) or isinstance(obj, BNode):
            continue
        if strip_volatile and str(pred) in _VOLATILE_RDF_PREDICATES:
            continue
        lines.append(f"{subj.n3()} {pred.n3()} {obj.n3()} .")
    body = "\n".join(sorted(lines)) + "\n"
    return _sha256_bytes(body.encode("utf-8"))


def write_rdf_artifact(
    path: Path, text: str, *, strip_volatile: bool = False
) -> str:
    """Write Turtle; keep existing bytes when ground-triple digest matches."""
    normalized = text.replace("\r\n", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    digest = rdf_ground_digest(normalized, strip_volatile=strip_volatile)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        existing = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        if rdf_ground_digest(existing, strip_volatile=strip_volatile) == digest:
            return digest
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return digest


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


def directory_tree_digest(directory: Path) -> str:
    """Stable digest over all files under directory (relative posix paths)."""
    h = hashlib.sha256()
    files = sorted(
        (p for p in directory.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(directory).as_posix().lower(),
    )
    for path in files:
        rel = path.relative_to(directory).as_posix()
        body = path.read_bytes()
        # Normalize text newlines when content is UTF-8 text.
        try:
            text = body.decode("utf-8").replace("\r\n", "\n")
            body = text.encode("utf-8")
        except UnicodeDecodeError:
            pass
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(body)
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
    generator_version = _linkml_version()
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        same = (
            existing.get("artifact_id") == artifact_id
            and existing.get("generator") == generator
            and existing.get("generator_module") == generator_module
            and existing.get("generator_version") == generator_version
            and existing.get("schema_path") == schema_rel()
            and existing.get("schema_digest") == schema_digest()
            and existing.get("output_path") == output_path
            and existing.get("content_digest") == content_digest
            and existing.get("generator_options") == generator_options
        )
        if same:
            return
    manifest: dict = {
        "artifact_id": artifact_id,
        "generator": generator,
        "generator_module": generator_module,
        "generator_version": generator_version,
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
        newline="\n",
    )


def generate_owl(*, out_path: Path = OWL_PATH, manifest_path: Path = OWL_MANIFEST) -> str:
    from linkml.generators.owlgen import OwlSchemaGenerator

    with schema_cwd() as schema_name:
        gen = OwlSchemaGenerator(schema_name, **OWL_OPTIONS)
        text = gen.serialize()
    digest = write_rdf_artifact(out_path, text)
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
        generator_options={
            **dict(OWL_OPTIONS),
            "digest_mode": "rdf_ground_triples",
        },
    )
    return digest


def generate_shacl(
    *, out_path: Path = SHACL_PATH, manifest_path: Path = SHACL_MANIFEST
) -> str:
    from linkml.generators.shaclgen import ShaclGenerator

    with schema_cwd() as schema_name:
        gen = ShaclGenerator(schema_name)
        text = gen.serialize()
    digest = write_rdf_artifact(out_path, text)
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
        generator_options={"digest_mode": "rdf_ground_triples"},
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


def generate_python(
    *, out_path: Path = PYTHON_PATH, manifest_path: Path = PYTHON_MANIFEST
) -> str:
    from linkml.generators.pythongen import PythonGenerator

    with schema_cwd() as schema_name:
        text = PythonGenerator(schema_name).serialize()
    digest = write_text_artifact(out_path, text, strip_generation_date=True)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-python:0.1",
        generator="gen-python",
        generator_module="linkml.generators.pythongen",
        output_path=out_rel,
        content_digest=digest,
        generator_options={"digest_mode": "strip_generation_date_comment"},
    )
    return digest

_DOC_README = """# DAMS gen-doc (LinkML)

Full Markdown set is produced by `make generate-artifacts` (or `moex-model compile --artifacts`).

**Git policy (`index_subset`):** only this `README.md` and `index.md` are committed.
Other `*.md` files are gitignored; regenerate locally or in CI for the full tree.
The golden `content_digest` in `generated/manifests/moex-dams-doc.json` covers the **full** generated tree (this README is written after digest and is not part of it).

Before `make generate-bundle` with staging, run a full doc generate so the staged bundle includes all pages.
"""


def generate_doc(
    *, out_dir: Path = DOC_DIR, manifest_path: Path = DOC_MANIFEST
) -> str:
    from linkml.generators.docgen import DocGenerator

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.rglob("*"):
        if old.is_file():
            old.unlink()

    with schema_cwd() as schema_name:
        DocGenerator(schema_name, directory=str(out_dir)).serialize()

    for path in out_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        except UnicodeDecodeError:
            continue
        if not body.endswith("\n"):
            body += "\n"
        path.write_text(body, encoding="utf-8", newline="\n")

    # Digest is DocGenerator output only; policy README is git-tracked but not golden.
    digest = directory_tree_digest(out_dir)
    readme = out_dir / "README.md"
    readme.write_text(_DOC_README.rstrip() + "\n", encoding="utf-8", newline="\n")

    try:
        out_rel = out_dir.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_dir.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-doc:0.1",
        generator="gen-doc",
        generator_module="linkml.generators.docgen",
        output_path=out_rel,
        content_digest=digest,
        generator_options={"git_policy": "index_subset"},
    )
    return digest


@contextmanager
def offline_jsonld_context_fetch() -> Iterator[None]:
    """Serve LinkML/DAMS JSON-LD contexts from disk — no HTTPS (CI/Docker SSL)."""
    import io
    import urllib.request
    from email.message import Message
    from urllib.response import addinfourl

    from linkml import LOCAL_METAMODEL_LDCONTEXT_FILE
    from linkml.generators.jsonldcontextgen import ContextGenerator

    types_ctx = Path(LOCAL_METAMODEL_LDCONTEXT_FILE).parent / "types.context.jsonld"
    schema_dir = SCHEMA.parent
    cache: dict[str, bytes] = {}
    if types_ctx.is_file():
        cache["https://w3id.org/linkml/types.context.jsonld"] = types_ctx.read_bytes()

    for yaml_path in sorted(schema_dir.glob("*.yaml")):
        stem = yaml_path.stem
        url = f"https://data.moex.com/dams/{stem}.context.jsonld"
        body = ContextGenerator(str(yaml_path)).serialize()
        cache[url] = body.encode("utf-8")

    def local_urlopen(req, *args, **kwargs):  # noqa: ANN001
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if url not in cache:
            raise RuntimeError(
                f"offline JSON-LD context miss: {url!r} "
                f"(known={sorted(cache)!r})"
            )
        headers = Message()
        headers["Content-Type"] = "application/ld+json"
        return addinfourl(io.BytesIO(cache[url]), headers, url, code=200)

    # rdflib.parser binds `_urlopen` at import — patch every alias that matters.
    import rdflib._networking as net
    import rdflib.parser as parser_mod

    patches: list[tuple[object, str, object]] = [
        (urllib.request, "urlopen", urllib.request.urlopen),
        (net, "urlopen", getattr(net, "urlopen", None)),
        (net, "_urlopen", net._urlopen),
        (parser_mod, "_urlopen", parser_mod._urlopen),
    ]
    for mod, name, _prev in patches:
        if _prev is not None:
            setattr(mod, name, local_urlopen)
    try:
        yield
    finally:
        for mod, name, prev in patches:
            if prev is not None:
                setattr(mod, name, prev)


def generate_rdf(
    *, out_path: Path = RDF_PATH, manifest_path: Path = RDF_MANIFEST
) -> str:
    from linkml import LOCAL_METAMODEL_LDCONTEXT_FILE
    from linkml.generators.rdfgen import RDFGenerator

    # Local metamodel context + offline fetch for import *.context.jsonld URLs
    # (rdflib otherwise hits HTTPS and fails under CI/Docker SSL interception).
    local_ctx = [LOCAL_METAMODEL_LDCONTEXT_FILE]
    with schema_cwd() as schema_name, offline_jsonld_context_fetch():
        text = RDFGenerator(schema_name, context=local_ctx).serialize(context=local_ctx)
    digest = write_rdf_artifact(out_path, text, strip_volatile=True)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-rdf:0.1",
        generator="gen-rdf",
        generator_module="linkml.generators.rdfgen",
        output_path=out_rel,
        content_digest=digest,
        generator_options={
            "digest_mode": "rdf_ground_triples",
            "strip_volatile": sorted(_VOLATILE_RDF_PREDICATES),
            "offline_jsonld_contexts": True,
        },
    )
    return digest


def generate_json_schema(
    *,
    out_path: Path = JSON_SCHEMA_PATH,
    manifest_path: Path = JSON_SCHEMA_MANIFEST,
) -> str:
    from linkml.generators.jsonschemagen import JsonSchemaGenerator

    with schema_cwd() as schema_name:
        text = JsonSchemaGenerator(schema_name).serialize()
    digest = write_text_artifact(out_path, text)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-json-schema:0.1",
        generator="gen-json-schema",
        generator_module="linkml.generators.jsonschemagen",
        output_path=out_rel,
        content_digest=digest,
    )
    return digest


def generate_ontology_report(
    *,
    out_path: Path = ONTOLOGY_PROFILE_PATH,
    manifest_path: Path = ONTOLOGY_PROFILE_MANIFEST,
    md_path: Path | None = None,
) -> str:
    """Regenerate Stage 8 ontology-profile.json (+ sibling .md)."""
    for rel in (
        "packages/specification-dams/src",
        "packages/modeling-kernel/src",
        "packages/standard-linkml/src",
        "generated/contracts/moex-dams/0.1",
    ):
        src = str(REPO / rel)
        if src not in sys.path:
            sys.path.insert(0, src)
    from moex_dams.application.ontology_report import write_ontology_profile

    md_out = md_path
    if md_out is None:
        if out_path == ONTOLOGY_PROFILE_PATH:
            md_out = ONTOLOGY_PROFILE_MD_PATH
        else:
            md_out = out_path.with_suffix(".md")
    digest = write_ontology_profile(SCHEMA, json_path=out_path, md_path=md_out)
    try:
        out_rel = out_path.relative_to(REPO).as_posix()
    except ValueError:
        out_rel = out_path.as_posix()
    write_manifest(
        path=manifest_path,
        artifact_id="moex:artifact:dams-ontology-profile:0.1",
        generator="ontology-report",
        generator_module="moex_dams.application.ontology_report",
        output_path=out_rel,
        content_digest=digest,
        generator_options={"digest_mode": "json_sorted"},
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
        elif target == "python":
            digests["python"] = generate_python()
        elif target == "doc":
            digests["doc"] = generate_doc()
        elif target == "rdf":
            digests["rdf"] = generate_rdf()
        elif target == "json-schema":
            digests["json-schema"] = generate_json_schema()
        elif target == "ontology-report":
            digests["ontology-report"] = generate_ontology_report()
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

    digests: dict[str, str] = {}
    try:
        for target in targets:
            digests.update(generate((target,)))
    except Exception as exc:
        failed = next((t for t in targets if t not in digests), "?")
        print(f"generate_artifacts failed at {failed}: {exc}", file=sys.stderr)
        return 1

    for name, digest in digests.items():
        print(f"{name}: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
