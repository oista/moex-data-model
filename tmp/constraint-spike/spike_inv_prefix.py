"""Spike (PR-C0): does an `INV-xxx:` prefix in a LinkML rule `description` change any golden artifact?

Copies the DAMS schema directory twice (A = as is, B = every rule description prefixed with INV-NNN),
runs every generator used by scripts/generate_artifacts.py + the pydantic contract generator on both
copies and compares outputs (generation-date lines stripped). The project tree is not modified;
work files live in tmp/constraint-spike/_work/ and are removed at the end.

Also reports which digests the golden manifests take from the *schema file*:
`schema_digest()` hashes only moex-dams.yaml (the root); imported modules are not part of it.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
SRC = REPO / "model-assets/specifications/moex-dams/0.1/schemas"
WORK = Path(__file__).resolve().parent / "_work"
DOC_FILES: dict[str, dict[str, str]] = {}


def strip(text: str) -> str:
    return "\n".join(l for l in text.replace("\r\n", "\n").split("\n") if not l.startswith("# Generation date:"))


def prefixed_copy(dst: Path) -> int:
    import inventory_invariants as inv

    shutil.copytree(SRC, dst)
    n = 0
    for k, (fname, cname, idx, desc) in enumerate(inv.list_rules(), start=1):
        p = dst / fname
        text = p.read_text(encoding="utf-8")
        needle = f"- description: {desc}"
        assert needle in text, (fname, desc)
        text = text.replace(needle, f"- description: 'INV-{k:03d}: {desc}'", 1)
        p.write_text(text, encoding="utf-8", newline="\n")
        n += 1
    return n


def run_generators(root: Path) -> dict[str, str]:
    from generate_artifacts import OWL_OPTIONS
    from linkml import LOCAL_METAMODEL_LDCONTEXT_FILE
    from linkml.generators.dbmlgen import DBMLGenerator
    from linkml.generators.docgen import DocGenerator
    from linkml.generators.jsonschemagen import JsonSchemaGenerator
    from linkml.generators.mermaidclassdiagramgen import MermaidClassDiagramGenerator
    from linkml.generators.owlgen import OwlSchemaGenerator
    from linkml.generators.pydanticgen import PydanticGenerator
    from linkml.generators.pythongen import PythonGenerator
    from linkml.generators.shaclgen import ShaclGenerator
    from rdflib import Graph
    from rdflib.compare import to_isomorphic

    out: dict[str, str] = {}
    prev = Path.cwd()
    os.chdir(root)
    try:
        s = "moex-dams.yaml"

        def rdf_digest(text: str) -> str:
            g = Graph()
            g.parse(data=text, format="turtle")
            triples = sorted(
                f"{a} {b} {c}" for a, b, c in g if "generation_date" not in str(b) and "generatedAtTime" not in str(b)
                and not any(type(t).__name__ == "BNode" for t in (a, b, c))
            )
            return hashlib.sha256("\n".join(triples).encode()).hexdigest()

        out["json-schema"] = JsonSchemaGenerator(s).serialize()
        from linkml.generators.pydanticgen.pydanticgen import MetadataMode  # same mode as scripts/generate_contracts.py

        out["pydantic(metadata NONE, as project)"] = PydanticGenerator(s, metadata_mode=MetadataMode.NONE).serialize()
        out["pydantic(default metadata)"] = PydanticGenerator(s).serialize()
        out["python"] = PythonGenerator(s).serialize()
        out["dbml"] = DBMLGenerator(s).serialize()
        out["owl"] = rdf_digest(OwlSchemaGenerator(s, **OWL_OPTIONS).serialize())
        out["shacl"] = rdf_digest(ShaclGenerator(s).serialize())
        d = root / "_doc"
        DocGenerator(s, directory=str(d)).serialize()
        out["doc"] = "\n".join(f"{p.relative_to(d)}\n{p.read_text(encoding='utf-8')}" for p in sorted(d.rglob("*")) if p.is_file())
        DOC_FILES[root.name] = {str(p.relative_to(d)): p.read_text(encoding="utf-8") for p in d.rglob("*") if p.is_file()}
        m = root / "_mermaid"
        m.mkdir()
        MermaidClassDiagramGenerator(s, directory=str(m)).serialize()
        out["mermaid"] = "\n".join(f"{p.name}\n{p.read_text(encoding='utf-8')}" for p in sorted(m.rglob("*")) if p.is_file())
    finally:
        os.chdir(prev)
    return {k: (v if len(v) == 64 else hashlib.sha256(strip(v).encode()).hexdigest()) for k, v in out.items()}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    a, b = WORK / "a", WORK / "b"
    shutil.copytree(SRC, a)
    n = prefixed_copy(b)
    try:
        ra, rb = run_generators(a), run_generators(b)
        root_a = hashlib.sha256((a / "moex-dams.yaml").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        root_b = hashlib.sha256((b / "moex-dams.yaml").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        print(f"rules prefixed: {n}")
        print(f"schema_digest basis (moex-dams.yaml root only): identical={root_a == root_b}")
        print("| artifact | content identical A vs B |")
        print("|---|---|")
        for k in ra:
            print(f"| {k} | {ra[k] == rb[k]} |")
        da, db = DOC_FILES["a"], DOC_FILES["b"]
        changed = sorted(k for k in set(da) | set(db) if da.get(k) != db.get(k))
        print(f"doc files differing: {len(changed)} of {len(da)}: {changed[:12]}")
        import difflib

        for k in changed[:3]:
            diff = list(difflib.unified_diff((da.get(k) or "").splitlines(), (db.get(k) or "").splitlines(), lineterm="", n=0))
            print("--", k, *diff[:8], sep="\n")
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
