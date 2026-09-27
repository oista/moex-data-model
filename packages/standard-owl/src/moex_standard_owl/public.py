"""Public API for standard-owl consumers (catalog composition root)."""

from __future__ import annotations

from moex_standard_owl.adapters.import_resolver import LocalImportResolver
from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_standard_owl.models import AggregatedEntity, EntityOccurrence, ParseError
from moex_standard_owl.provider import OntologyProvider, try_get_oak_adapter
from moex_standard_owl.rdf_parser import local_name_from_iri, parse_rdf_file

__all__ = [
    "AggregatedEntity",
    "EntityOccurrence",
    "LocalImportResolver",
    "OntologyProvider",
    "ParseError",
    "RdflibOntologyAdapter",
    "local_name_from_iri",
    "parse_rdf_file",
    "try_get_oak_adapter",
]
