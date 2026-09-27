"""RDFLib-backed OntologyProvider over one or more local RDF files."""

from __future__ import annotations

from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef

from moex_standard_owl.constants import DCTERMS, SKOS
from moex_standard_owl.literals import preferred_literal_values
from moex_standard_owl.rdf_parser import local_name_from_iri


RDFS_SUBCLASS = str(RDFS.subClassOf)


class RdflibOntologyAdapter:
    """Offline provider: load RDF files into a single graph (no import fetch)."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._entity_iris: tuple[str, ...] | None = None

    @classmethod
    def from_directory(
        cls,
        root: Path,
        *,
        patterns: tuple[str, ...] = ("*.rdf", "*.owl", "*.ttl"),
    ) -> RdflibOntologyAdapter:
        root = root.expanduser().resolve()
        graph = Graph()
        files: list[Path] = []
        for pattern in patterns:
            files.extend(root.rglob(pattern))
        for path in sorted(set(files)):
            if not path.is_file():
                continue
            # Skip known broken fixture files by name convention
            try:
                fmt = "turtle" if path.suffix.lower() in {".ttl", ".turtle"} else "xml"
                graph.parse(str(path), format=fmt)
            except Exception:
                continue
        return cls(graph)

    @classmethod
    def from_files(cls, paths: list[Path]) -> RdflibOntologyAdapter:
        graph = Graph()
        for path in paths:
            fmt = "turtle" if path.suffix.lower() in {".ttl", ".turtle"} else "xml"
            try:
                graph.parse(str(path), format=fmt)
            except Exception:
                continue
        return cls(graph)

    def label(self, iri: str) -> str | None:
        nodes = list(self._graph.objects(URIRef(iri), RDFS.label))
        value, _ = preferred_literal_values(nodes)
        return value

    def definition(self, iri: str) -> str | None:
        subject = URIRef(iri)
        for predicate in (SKOS.definition, DCTERMS.description, SKOS.scopeNote):
            nodes = list(self._graph.objects(subject, predicate))
            value, _ = preferred_literal_values(nodes)
            if value is not None:
                return value
        return None

    def aliases(self, iri: str) -> tuple[str, ...]:
        subject = URIRef(iri)
        texts: list[str] = []
        seen: set[str] = set()
        primary = self.label(iri)
        if primary:
            seen.update(p.strip() for p in primary.split(" | "))
        for predicate in (SKOS.prefLabel, SKOS.altLabel, RDFS.label):
            for node in self._graph.objects(subject, predicate):
                if not isinstance(node, Literal):
                    continue
                text = str(node).strip()
                if text and text not in seen:
                    seen.add(text)
                    texts.append(text)
        return tuple(texts)

    def parents(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]:
        pred = _predicate_uri(predicate)
        result: list[str] = []
        for obj in self._graph.objects(URIRef(iri), pred):
            if isinstance(obj, URIRef):
                result.append(str(obj))
        return tuple(sorted(set(result)))

    def children(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]:
        pred = _predicate_uri(predicate)
        result: list[str] = []
        for subj in self._graph.subjects(pred, URIRef(iri)):
            if isinstance(subj, URIRef):
                result.append(str(subj))
        return tuple(sorted(set(result)))

    def search(self, query: str, *, limit: int = 50) -> tuple[str, ...]:
        q = query.strip().lower()
        if not q:
            return ()
        hits: list[str] = []
        for iri in self.entities():
            label = (self.label(iri) or "").lower()
            local = local_name_from_iri(iri).lower()
            definition = (self.definition(iri) or "").lower()
            aliases = " ".join(self.aliases(iri)).lower()
            if q in label or q in local or q in definition or q in aliases:
                hits.append(iri)
            if len(hits) >= limit:
                break
        return tuple(hits)

    def entities(self) -> tuple[str, ...]:
        if self._entity_iris is not None:
            return self._entity_iris
        iris: set[str] = set()
        for owl_type in (
            OWL.Class,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            OWL.NamedIndividual,
        ):
            for subj in self._graph.subjects(RDF.type, owl_type):
                if isinstance(subj, URIRef):
                    iris.add(str(subj))
        self._entity_iris = tuple(sorted(iris))
        return self._entity_iris

    def domain_range(self, iri: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        subject = URIRef(iri)
        domains = [
            str(o) for o in self._graph.objects(subject, RDFS.domain) if isinstance(o, URIRef)
        ]
        ranges = [
            str(o) for o in self._graph.objects(subject, RDFS.range) if isinstance(o, URIRef)
        ]
        return tuple(sorted(set(domains))), tuple(sorted(set(ranges)))


def _predicate_uri(predicate: str) -> URIRef:
    if predicate in {"rdfs:subClassOf", RDFS_SUBCLASS, str(RDFS.subClassOf)}:
        return RDFS.subClassOf
    if predicate.startswith("http://") or predicate.startswith("https://"):
        return URIRef(predicate)
    if predicate == "rdfs:subPropertyOf":
        return RDFS.subPropertyOf
    return URIRef(predicate)
