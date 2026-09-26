"""Shared RDF/OWL namespaces and entity-type codes."""

from __future__ import annotations

from rdflib import OWL, RDF, RDFS, Namespace, URIRef

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCTERMS = Namespace("http://purl.org/dc/terms/")

# Internal type codes used by CLI / filters
TYPE_CLASS = "class"
TYPE_OBJECT_PROPERTY = "object_property"
TYPE_DATATYPE_PROPERTY = "datatype_property"
TYPE_ANNOTATION_PROPERTY = "annotation_property"
TYPE_INDIVIDUAL = "individual"

DEFAULT_ENTITY_TYPES: tuple[str, ...] = (
    TYPE_CLASS,
    TYPE_OBJECT_PROPERTY,
    TYPE_DATATYPE_PROPERTY,
    TYPE_ANNOTATION_PROPERTY,
)

ALL_ENTITY_TYPES: tuple[str, ...] = DEFAULT_ENTITY_TYPES + (TYPE_INDIVIDUAL,)

# Display / export values matching OWL vocabulary
ENTITY_TYPE_OWL: dict[str, str] = {
    TYPE_CLASS: "owl:Class",
    TYPE_OBJECT_PROPERTY: "owl:ObjectProperty",
    TYPE_DATATYPE_PROPERTY: "owl:DatatypeProperty",
    TYPE_ANNOTATION_PROPERTY: "owl:AnnotationProperty",
    TYPE_INDIVIDUAL: "owl:NamedIndividual",
}

OWL_TYPE_TO_CODE: dict[URIRef, str] = {
    OWL.Class: TYPE_CLASS,
    OWL.ObjectProperty: TYPE_OBJECT_PROPERTY,
    OWL.DatatypeProperty: TYPE_DATATYPE_PROPERTY,
    OWL.AnnotationProperty: TYPE_ANNOTATION_PROPERTY,
    OWL.NamedIndividual: TYPE_INDIVIDUAL,
}

CODE_TO_OWL_URI: dict[str, URIRef] = {v: k for k, v in OWL_TYPE_TO_CODE.items()}

OUTPUT_FORMATS: tuple[str, ...] = ("csv", "xlsx", "json")
DEFAULT_OUTPUT_FORMATS: tuple[str, ...] = ("csv", "xlsx")

LABEL_JOIN = " | "
DEFINITION_JOIN = "\n---\n"
MODULE_JOIN = " | "
SUPERCLASS_JOIN = " | "
SHA_JOIN = " | "

NULL_SENTINEL = None  # empty CSV/Excel cell; JSON null

__all__ = [
    "SKOS",
    "DCTERMS",
    "RDF",
    "RDFS",
    "OWL",
    "TYPE_CLASS",
    "TYPE_OBJECT_PROPERTY",
    "TYPE_DATATYPE_PROPERTY",
    "TYPE_ANNOTATION_PROPERTY",
    "TYPE_INDIVIDUAL",
    "DEFAULT_ENTITY_TYPES",
    "ALL_ENTITY_TYPES",
    "ENTITY_TYPE_OWL",
    "OWL_TYPE_TO_CODE",
    "CODE_TO_OWL_URI",
    "OUTPUT_FORMATS",
    "DEFAULT_OUTPUT_FORMATS",
    "LABEL_JOIN",
    "DEFINITION_JOIN",
    "MODULE_JOIN",
    "SUPERCLASS_JOIN",
    "SHA_JOIN",
    "NULL_SENTINEL",
]
