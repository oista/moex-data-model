"""CLI: rebuild ontology index and export viewer preview JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_semantic_mappings.sssom_adapter import load_sssom_yaml

from moex_ontology.adapters.binding_repo import MappingSetBindingRepository
from moex_ontology.adapters.sqlite_index import SqliteOntologyIndex
from moex_ontology.application.ingest import ingest_release_from_directory
from moex_ontology.application.list_ontologies import list_ontologies
from moex_ontology.application.search_entities import search_entities
from moex_ontology.domain.release import load_release_descriptors
from moex_ontology.publication_export import export_preview_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moex-ontology-catalog")
    sub = parser.add_subparsers(dest="command", required=True)

    rebuild = sub.add_parser("rebuild", help="Rebuild SQLite index from descriptors + source")
    rebuild.add_argument("--descriptors", type=Path, required=True)
    rebuild.add_argument("--source", type=Path, required=True, help="Local RDF root (e.g. mini_fibo)")
    rebuild.add_argument("--db", type=Path, required=True)
    rebuild.add_argument("--preview-out", type=Path, default=None)
    rebuild.add_argument(
        "--sssom",
        type=Path,
        default=None,
        help="Optional SSSOM YAML for backlinks in preview export",
    )
    rebuild.add_argument(
        "--index-id",
        default="moex:ontology:fibo",
        help="Descriptor id to ingest from --source (others stay registered stubs)",
    )
    rebuild.add_argument(
        "--domains",
        default="FND,BE",
        help="FIBO-style domains to scan under --source",
    )
    return parser


def cmd_rebuild(args: argparse.Namespace) -> int:
    releases = load_release_descriptors(args.descriptors)
    if not releases:
        print(f"No descriptors in {args.descriptors}", file=sys.stderr)
        return 2

    entities = []
    relations = []
    updated: list = []
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    for release in releases:
        if release.id == args.index_id:
            indexed, ents, rels = ingest_release_from_directory(
                release, args.source, domains=domains
            )
            updated.append(indexed)
            entities.extend(ents)
            relations.extend(rels)
        else:
            updated.append(release)

    index = SqliteOntologyIndex(args.db)
    index.replace_all(releases=updated, entities=entities, relations=relations)

    provider = RdflibOntologyAdapter.from_directory(args.source)
    bindings = None
    if args.sssom and Path(args.sssom).is_file():
        bindings = MappingSetBindingRepository(load_sssom_yaml(args.sssom))

    print(f"Indexed {len(entities)} entities, {len(relations)} relations -> {args.db}")

    if args.preview_out:
        export_preview_json(
            args.preview_out,
            index=index,
            provider=provider,
            bindings=bindings,
        )
        print(f"Wrote preview JSON under {args.preview_out}")

    summaries = list_ontologies(index)
    print(f"Releases: {len(summaries)}")
    hits = search_entities(index, "Legal", limit=5)
    print(f"Search 'Legal': {len(hits)} hit(s)")
    index.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "rebuild":
        return cmd_rebuild(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
