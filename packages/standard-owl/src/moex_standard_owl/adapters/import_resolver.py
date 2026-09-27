"""Resolve owl:imports only against a local checkout (no network)."""

from __future__ import annotations

from pathlib import Path

from rdflib import OWL, RDF, Graph, URIRef


class LocalImportResolver:
    """Map ontology IRIs to files under a local root; never fetch HTTP."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser().resolve()
        self._iri_to_path: dict[str, Path] = {}
        self._index()

    def _index(self) -> None:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".rdf", ".owl", ".ttl", ".n3", ".nt"}:
                continue
            try:
                graph = Graph()
                fmt = _guess_format(path)
                graph.parse(str(path), format=fmt)
            except Exception:
                continue
            for subj in graph.subjects(RDF.type, OWL.Ontology):
                if isinstance(subj, URIRef):
                    self._iri_to_path[str(subj)] = path

    def resolve(self, ontology_iri: str) -> Path | None:
        if ontology_iri in self._iri_to_path:
            return self._iri_to_path[ontology_iri]
        # Soft match: trailing slash variants
        alt = ontology_iri.rstrip("/") + "/"
        return self._iri_to_path.get(alt) or self._iri_to_path.get(ontology_iri.rstrip("/"))

    def list_imports(self, path: Path) -> tuple[str, ...]:
        graph = Graph()
        graph.parse(str(path), format=_guess_format(path))
        iris: list[str] = []
        for ontology in graph.subjects(RDF.type, OWL.Ontology):
            for obj in graph.objects(ontology, OWL.imports):
                if isinstance(obj, URIRef):
                    iris.append(str(obj))
        return tuple(sorted(set(iris)))


def _guess_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".ttl", ".turtle"}:
        return "turtle"
    if suffix in {".nt"}:
        return "nt"
    if suffix in {".n3"}:
        return "n3"
    return "xml"
