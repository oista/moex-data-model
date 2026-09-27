"""OAK (oaklib) adapter — optional dependency ``moex-standard-owl[oak]``."""

from __future__ import annotations

from pathlib import Path

from oaklib import get_adapter
from oaklib.interfaces.basic_ontology_interface import BasicOntologyInterface
from oaklib.interfaces.search_interface import SearchInterface

from moex_standard_owl.rdf_parser import local_name_from_iri


class OakOntologyAdapter:
    """Wrap oaklib rdflib:/sqlite: implementations behind OntologyProvider."""

    def __init__(self, source: Path | str) -> None:
        path = Path(source).expanduser().resolve()
        if path.is_dir():
            # Prefer a single combined turtle/rdf if present; else first rdf
            candidates = sorted(path.rglob("*.rdf")) + sorted(path.rglob("*.owl"))
            if not candidates:
                raise FileNotFoundError(f"No RDF/OWL files under {path}")
            # Load directory via rdflib multipath is not native — use first file
            # and rely on catalog index for multi-file; OAK single-file handle.
            handle = f"rdflib:{candidates[0]}"
        else:
            handle = f"rdflib:{path}"
        adapter = get_adapter(handle)
        if not isinstance(adapter, BasicOntologyInterface):
            raise TypeError(f"Unexpected OAK adapter type: {type(adapter)}")
        self._adapter: BasicOntologyInterface = adapter

    def label(self, iri: str) -> str | None:
        return self._adapter.label(iri)

    def definition(self, iri: str) -> str | None:
        try:
            return self._adapter.definition(iri)
        except Exception:
            return None

    def aliases(self, iri: str) -> tuple[str, ...]:
        try:
            vals = list(self._adapter.entity_aliases(iri) or [])
        except Exception:
            vals = []
        return tuple(v for v in vals if v)

    def parents(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]:
        preds = _oak_predicates(predicate)
        result: list[str] = []
        for pred in preds:
            try:
                result.extend(self._adapter.hierarchical_parents(iri, predicates=[pred]))
            except Exception:
                try:
                    result.extend(self._adapter.outgoing_relationship_map(iri).get(pred, []))
                except Exception:
                    pass
        return tuple(sorted(set(result)))

    def children(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]:
        preds = _oak_predicates(predicate)
        result: list[str] = []
        for pred in preds:
            try:
                result.extend(self._adapter.hierarchical_children(iri, predicates=[pred]))
            except Exception:
                pass
        return tuple(sorted(set(result)))

    def search(self, query: str, *, limit: int = 50) -> tuple[str, ...]:
        if isinstance(self._adapter, SearchInterface):
            try:
                hits = list(self._adapter.basic_search(query))
                return tuple(hits[:limit])
            except Exception:
                pass
        # Fallback substring over curated entities
        q = query.strip().lower()
        hits: list[str] = []
        for iri in self.entities():
            label = (self.label(iri) or "").lower()
            if q in label or q in local_name_from_iri(iri).lower():
                hits.append(iri)
            if len(hits) >= limit:
                break
        return tuple(hits)

    def entities(self) -> tuple[str, ...]:
        try:
            return tuple(sorted(self._adapter.entities(filter_obsoletes=False)))
        except Exception:
            return ()


def _oak_predicates(predicate: str) -> list[str]:
    if predicate in {"rdfs:subClassOf", "subClassOf"}:
        return ["rdfs:subClassOf", "http://www.w3.org/2000/01/rdf-schema#subClassOf"]
    return [predicate]
