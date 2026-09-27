"""OntologyProvider protocol and factory helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter


@runtime_checkable
class OntologyProvider(Protocol):
    """Read-only access to labels, definitions, and asserted hierarchy."""

    def label(self, iri: str) -> str | None: ...

    def definition(self, iri: str) -> str | None: ...

    def aliases(self, iri: str) -> tuple[str, ...]: ...

    def parents(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]: ...

    def children(self, iri: str, *, predicate: str = "rdfs:subClassOf") -> tuple[str, ...]: ...

    def search(self, query: str, *, limit: int = 50) -> tuple[str, ...]: ...

    def entities(self) -> tuple[str, ...]: ...


def try_get_oak_adapter(source: Path | str) -> OntologyProvider | None:
    """Return an OAK rdflib adapter when oaklib is installed; else None."""
    try:
        from moex_standard_owl.adapters.oak_adapter import OakOntologyAdapter
    except ImportError:
        return None
    return OakOntologyAdapter(source)


def get_provider(source: Path | str, *, prefer_oak: bool = True) -> OntologyProvider:
    """Prefer OAK when available; otherwise RDFLib adapter over local files."""
    path = Path(source)
    if prefer_oak:
        oak = try_get_oak_adapter(path)
        if oak is not None:
            return oak
    return RdflibOntologyAdapter.from_directory(path)
