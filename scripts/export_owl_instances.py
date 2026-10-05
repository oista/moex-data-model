"""Optional linkml-owl instance export smoke (Stage 8 / ADR-030).

Usage (from repo root, with apps/cli[ontology] installed):
  python scripts/export_owl_instances.py
  python scripts/export_owl_instances.py --out tmp/owl-instances.ttl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_INSTANCE = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "ontology"
    / "valid-model-package.yaml"
)
DEFAULT_SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO / "tmp" / "owl-instances.ttl",
    )
    args = parser.parse_args(argv)

    try:
        import linkml_owl  # noqa: F401
    except ImportError:
        print(
            "linkml-owl is not installed. Install Stage 8 ontology extras:\n"
            "  pip install -r requirements-ontology.txt\n"
            "  # or: pip install -e \"./apps/cli[ontology]\"",
            file=sys.stderr,
        )
        return 2

    # Prefer RDFLibDumper path when linkml-owl API is unavailable / unstable;
    # still require the package so the optional dependency is exercised.
    sys.path.insert(0, str(REPO / "generated" / "artifacts" / "moex-dams" / "0.1" / "python"))
    from linkml_runtime import SchemaView
    from linkml_runtime.dumpers.rdflib_dumper import RDFLibDumper
    from linkml_runtime.loaders import yaml_loader
    from moex_dams import ModelPackage

    sv = SchemaView(str(args.schema))
    obj = yaml_loader.load(str(args.instance), target_class=ModelPackage)
    graph = RDFLibDumper().as_rdf_graph(obj, schemaview=sv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(graph.serialize(format="turtle"), encoding="utf-8", newline="\n")
    print(f"owl-instances: wrote {args.out} (linkml-owl installed; dump via RDFLibDumper)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
