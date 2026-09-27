"""Parse a single RDF/OWL file into entity occurrences."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef
from rdflib.term import Node

from moex_standard_owl.constants import (
    DCTERMS,
    DEFINITION_JOIN,
    ENTITY_TYPE_OWL,
    LABEL_JOIN,
    MODULE_JOIN,
    OWL_TYPE_TO_CODE,
    SKOS,
    SUPERCLASS_JOIN,
    TYPE_CLASS,
)
from moex_standard_owl.literals import join_unique, preferred_literal_values
from moex_standard_owl.models import EntityOccurrence, ParseError

logger = logging.getLogger(__name__)


def local_name_from_iri(iri: str) -> str:
    """Extract local name: fragment after #, else last path segment after /."""
    if "#" in iri:
        frag = iri.rsplit("#", 1)[-1]
        if frag:
            return frag
    return iri.rstrip("/").rsplit("/", 1)[-1]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_true_literal(node: Node) -> bool:
    if isinstance(node, Literal):
        # xsd:boolean true / "true" / "1"
        try:
            return bool(node.toPython()) is True and (
                isinstance(node.toPython(), bool)
                or str(node).lower() in {"true", "1"}
            )
        except Exception:
            return str(node).strip().lower() in {"true", "1"}
    if isinstance(node, URIRef):
        return str(node) in {
            "http://www.w3.org/2001/XMLSchema#true",
            str(Literal(True)),
        }
    return False


def _collect_texts(graph: Graph, subject: URIRef, predicate: URIRef) -> list[Node]:
    return list(graph.objects(subject, predicate))


def _extract_definition(
    graph: Graph, subject: URIRef
) -> tuple[str | None, str | None]:
    """skos:definition → dcterms:description → skos:scopeNote."""
    for predicate in (SKOS.definition, DCTERMS.description, SKOS.scopeNote):
        nodes = _collect_texts(graph, subject, predicate)
        value, lang = preferred_literal_values(nodes, join=DEFINITION_JOIN)
        if value is not None:
            return value, lang
    return None, None


def _extract_label(
    graph: Graph, subject: URIRef
) -> tuple[str | None, str | None, str | None]:
    """
    Returns (primary_label, label_language, alternative_labels).

    Primary label from rdfs:label (en / neutral preference).
    Alternatives: skos:prefLabel, skos:altLabel, and extra rdfs:label values
    not already in the primary label field.
    """
    rdfs_labels = _collect_texts(graph, subject, RDFS.label)
    primary, primary_lang = preferred_literal_values(rdfs_labels, join=LABEL_JOIN)

    primary_parts: set[str] = set()
    if primary:
        primary_parts = {p.strip() for p in primary.split(LABEL_JOIN)}

    alt_nodes: list[Node] = []
    alt_nodes.extend(_collect_texts(graph, subject, SKOS.prefLabel))
    alt_nodes.extend(_collect_texts(graph, subject, SKOS.altLabel))

    # rdfs:label values that did not make it into the preferred primary set
    # (e.g. non-English when English exists) — treat as alternatives
    for node in rdfs_labels:
        if not isinstance(node, Literal):
            continue
        text = str(node).strip()
        if text and text not in primary_parts:
            alt_nodes.append(node)

    alt_value, _ = preferred_literal_values(alt_nodes, join=LABEL_JOIN)
    # Also keep non-preferred language labels even if preferred_literal_values
    # would drop them when en exists among alts — collect all unique alt texts
    alt_texts: list[str] = []
    seen: set[str] = set()
    for node in alt_nodes:
        if not isinstance(node, Literal):
            continue
        text = str(node).strip()
        if not text or text in primary_parts or text in seen:
            continue
        seen.add(text)
        alt_texts.append(text)
    alt_joined = LABEL_JOIN.join(alt_texts) if alt_texts else None
    # Prefer exhaustive alt list over language-filtered one when both exist
    if alt_joined:
        alt_value = alt_joined

    return primary, primary_lang, alt_value


def _is_deprecated(graph: Graph, subject: URIRef) -> bool:
    for obj in graph.objects(subject, OWL.deprecated):
        if _is_true_literal(obj):
            return True
    return False


def _deprecated_replacement(graph: Graph, subject: URIRef) -> str | None:
    """Only dcterms:isReplacedBy — no heuristics."""
    replacements: list[str] = []
    for obj in graph.objects(subject, DCTERMS.isReplacedBy):
        if isinstance(obj, URIRef):
            replacements.append(str(obj))
    return join_unique(replacements, LABEL_JOIN)


def _superclasses(graph: Graph, subject: URIRef) -> str | None:
    uris: list[str] = []
    for obj in graph.objects(subject, RDFS.subClassOf):
        if isinstance(obj, URIRef):
            uris.append(str(obj))
    return join_unique(uris, SUPERCLASS_JOIN)


def _module_iris(graph: Graph) -> str | None:
    iris: list[str] = []
    for subj in graph.subjects(RDF.type, OWL.Ontology):
        if isinstance(subj, URIRef):
            iris.append(str(subj))
    return join_unique(iris, MODULE_JOIN)


def _version_iris(graph: Graph) -> str | None:
    iris: list[str] = []
    for ontology in graph.subjects(RDF.type, OWL.Ontology):
        for obj in graph.objects(ontology, OWL.versionIRI):
            if isinstance(obj, URIRef):
                iris.append(str(obj))
    return join_unique(iris, MODULE_JOIN)


def _imports(graph: Graph) -> str | None:
    iris: list[str] = []
    for ontology in graph.subjects(RDF.type, OWL.Ontology):
        for obj in graph.objects(ontology, OWL.imports):
            if isinstance(obj, URIRef):
                iris.append(str(obj))
    return join_unique(iris, MODULE_JOIN)


def parse_rdf_file(
    path: Path,
    *,
    module_path: str,
    source_release: str,
    source_domain: str | None = None,
    entity_type_codes: set[str] | None = None,
) -> tuple[list[EntityOccurrence], ParseError | None]:
    """
    Parse one RDF/XML file.

    Returns (occurrences, parse_error). On success parse_error is None.
    Does not resolve owl:imports or make network requests.
    """
    sha = file_sha256(path)
    try:
        graph = Graph()
        # Local file path only — do not resolve owl:imports / network
        graph.parse(str(path), format="xml")
    except Exception as exc:  # noqa: BLE001 — surface any parse failure
        err = ParseError(
            module_path=module_path,
            exception_type=type(exc).__name__,
            exception_message=str(exc),
        )
        logger.error("Failed to parse %s: %s: %s", module_path, type(exc).__name__, exc)
        return [], err

    module_iri = _module_iris(graph)
    version_iri = _version_iris(graph)
    imports = _imports(graph)

    allowed = entity_type_codes  # None = extract all known OWL types
    occurrences: list[EntityOccurrence] = []
    seen_keys: set[tuple[str, str]] = set()

    for owl_type, code in OWL_TYPE_TO_CODE.items():
        if allowed is not None and code not in allowed:
            continue
        owl_name = ENTITY_TYPE_OWL[code]
        for subject in graph.subjects(RDF.type, owl_type):
            if not isinstance(subject, URIRef):
                continue  # skip blank nodes
            iri = str(subject)
            key = (iri, owl_name)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            label, label_lang, alt_labels = _extract_label(graph, subject)
            definition, def_lang = _extract_definition(graph, subject)
            deprecated = _is_deprecated(graph, subject)
            replacement = _deprecated_replacement(graph, subject) if deprecated else None
            supers = _superclasses(graph, subject) if code == TYPE_CLASS else None

            occurrences.append(
                EntityOccurrence(
                    iri=iri,
                    local_name=local_name_from_iri(iri),
                    label=label,
                    definition=definition,
                    entity_type=owl_name,
                    entity_type_code=code,
                    module_iri=module_iri,
                    module_path=module_path,
                    is_deprecated=deprecated,
                    deprecated_replacement_iri=replacement,
                    superclasses=supers,
                    source_release=source_release,
                    source_file_sha256=sha,
                    alternative_labels=alt_labels,
                    definition_language=def_lang,
                    label_language=label_lang,
                    ontology_version_iri=version_iri,
                    imports=imports,
                    source_domain=source_domain,
                    parse_status="ok",
                    parse_error=None,
                )
            )

    return occurrences, None
