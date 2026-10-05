"""Stable text/digest helpers for golden artifacts and the publish gate."""

from __future__ import annotations

import hashlib
from pathlib import Path

VOLATILE_RDF_PREDICATES = frozenset(
    {
        "https://w3id.org/linkml/generation_date",
        "http://www.w3.org/ns/prov#generatedAtTime",
    }
)


def strip_generation_date_lines(text: str) -> str:
    """Drop LinkML '# Generation date: …' comment lines for stable digests."""
    lines = [
        line
        for line in text.split("\n")
        if not line.startswith("# Generation date:")
    ]
    return "\n".join(lines)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def lf_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def file_digest(path: Path) -> str:
    return sha256_text(lf_text(path))


def python_artifact_digest(path: Path) -> str:
    return sha256_text(strip_generation_date_lines(lf_text(path)))


def mermaid_tree_digest(directory: Path) -> str:
    h = hashlib.sha256()
    files = sorted(directory.glob("*.md"), key=lambda p: p.name.lower())
    for path in files:
        body = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(body.encode("utf-8"))
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def directory_tree_digest(directory: Path) -> str:
    h = hashlib.sha256()
    files = sorted(
        (p for p in directory.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(directory).as_posix().lower(),
    )
    for path in files:
        rel = path.relative_to(directory).as_posix()
        body = path.read_bytes()
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


def rdf_ground_digest(text: str, *, strip_volatile: bool = False) -> str:
    from rdflib import BNode, Graph

    graph = Graph()
    graph.parse(data=text, format="turtle")
    lines: list[str] = []
    for subj, pred, obj in graph:
        if isinstance(subj, BNode) or isinstance(obj, BNode):
            continue
        if strip_volatile and str(pred) in VOLATILE_RDF_PREDICATES:
            continue
        lines.append(f"{subj.n3()} {pred.n3()} {obj.n3()} .")
    body = "\n".join(sorted(lines)) + "\n"
    return sha256_bytes(body.encode("utf-8"))


def artifact_paths(root: Path) -> dict[str, Path]:
    """Canonical golden paths under a repo root."""
    arts = root / "generated" / "artifacts" / "moex-dams" / "0.1"
    mans = root / "generated" / "manifests"
    return {
        "owl": arts / "moex-dams.owl.ttl",
        "owl_manifest": mans / "moex-dams-owl.json",
        "shacl": arts / "moex-dams.shacl.ttl",
        "shacl_manifest": mans / "moex-dams-shacl.json",
        "dbml": arts / "moex-dams.dbml",
        "dbml_manifest": mans / "moex-dams-dbml.json",
        "mermaid": arts / "diagrams",
        "mermaid_manifest": mans / "moex-dams-mermaid.json",
        "python": arts / "python" / "moex_dams.py",
        "python_manifest": mans / "moex-dams-python.json",
        "doc": arts / "docs",
        "doc_manifest": mans / "moex-dams-doc.json",
        "rdf": arts / "moex-dams.rdf.ttl",
        "rdf_manifest": mans / "moex-dams-rdf.json",
        "json_schema": arts / "moex-dams.schema.json",
        "json_schema_manifest": mans / "moex-dams-json-schema.json",
        "ontology_profile": arts / "ontology-profile.json",
        "ontology_profile_md": arts / "ontology-profile.md",
        "ontology_profile_manifest": mans / "moex-dams-ontology-profile.json",
        "bundle_manifest": mans / "moex-dams-bundle.json",
    }


__all__ = [
    "VOLATILE_RDF_PREDICATES",
    "artifact_paths",
    "directory_tree_digest",
    "file_digest",
    "lf_text",
    "mermaid_tree_digest",
    "python_artifact_digest",
    "rdf_ground_digest",
    "sha256_bytes",
    "sha256_text",
    "strip_generation_date_lines",
]
