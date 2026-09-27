"""Ingest local RDF into OntologyEntity / OntologyRelation lists."""

from __future__ import annotations

from pathlib import Path

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_standard_owl.fibo.discovery import discover_rdf_files
from moex_standard_owl.rdf_parser import parse_rdf_file

from moex_ontology.domain.entity import OntologyEntity, OntologyEntityKind
from moex_ontology.domain.ontology import OntologyRelease
from moex_ontology.domain.relation import OntologyRelation

KIND_MAP: dict[str, OntologyEntityKind] = {
    "class": "class",
    "object_property": "object_property",
    "datatype_property": "data_property",
    "annotation_property": "annotation_property",
    "individual": "individual",
}


def ingest_release_from_directory(
    release: OntologyRelease,
    source_root: Path,
    *,
    domains: list[str] | None = None,
) -> tuple[OntologyRelease, list[OntologyEntity], list[OntologyRelation]]:
    """
    Parse RDF under ``source_root`` into catalog entities/relations.

    When ``domains`` is set, uses FIBO-style domain discovery; otherwise loads
    all ``*.rdf`` / ``*.owl`` files found under the root.
    """
    source_root = source_root.expanduser().resolve()
    occurrences = []
    ok_paths: list[Path] = []
    if domains:
        files = discover_rdf_files(source_root, domains, include_examples=False)
        for discovered in files:
            occs, err = parse_rdf_file(
                discovered.path,
                module_path=discovered.module_path,
                source_release=release.version,
                source_domain=discovered.domain,
            )
            if err is None:
                occurrences.extend(occs)
                ok_paths.append(discovered.path)
    else:
        paths = sorted(
            set(source_root.rglob("*.rdf")) | set(source_root.rglob("*.owl"))
        )
        for path in paths:
            if not path.is_file():
                continue
            rel = path.relative_to(source_root).as_posix()
            occs, err = parse_rdf_file(
                path,
                module_path=rel,
                source_release=release.version,
            )
            if err is None:
                occurrences.extend(occs)
                ok_paths.append(path)

    entities_by_iri: dict[str, OntologyEntity] = {}
    for occ in occurrences:
        kind = KIND_MAP.get(occ.entity_type_code)
        if kind is None:
            continue
        alts = tuple(
            a.strip()
            for a in (occ.alternative_labels or "").split(" | ")
            if a.strip()
        )
        entities_by_iri[occ.iri] = OntologyEntity(
            iri=occ.iri,
            ontology_id=release.id,
            kind=kind,
            label=occ.label,
            definition=occ.definition,
            alternative_labels=alts,
            deprecated=occ.is_deprecated,
            replaced_by=occ.deprecated_replacement_iri,
        )

    adapter = (
        RdflibOntologyAdapter.from_files(ok_paths)
        if ok_paths
        else RdflibOntologyAdapter.from_directory(source_root)
    )
    relations: list[OntologyRelation] = []
    for iri, ent in entities_by_iri.items():
        if ent.kind != "class":
            continue
        for parent in adapter.parents(iri):
            relations.append(
                OntologyRelation(
                    subject=iri,
                    predicate="rdfs:subClassOf",
                    object=parent,
                    asserted=True,
                    source_ontology=release.id,
                )
            )

    indexed = release.model_copy(
        update={
            "status": "indexed",
            "content_digest": release.content_digest or "sha256:local-preview",
        }
    )
    return indexed, list(entities_by_iri.values()), relations
