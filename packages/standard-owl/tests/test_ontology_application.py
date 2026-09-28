"""Ontology application descriptor tests (ADR-018)."""

from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph

from moex_standard_owl.domain.ontology_application import (
    OntologyApplicationDescriptor,
    load_ontology_application_descriptor,
)
from moex_standard_owl.public import OntologyApplicationDescriptor as PublicDescriptor

REPO = Path(__file__).resolve().parents[3]
APP_DIR = (
    REPO
    / "model-assets"
    / "implementations"
    / "ontologies"
    / "moex-fibo-application"
    / "0.1"
)
DESCRIPTOR = APP_DIR / "ontology-application.yaml"


def test_load_ontology_application_descriptor_from_assets() -> None:
    desc = load_ontology_application_descriptor(DESCRIPTOR)
    assert isinstance(desc, OntologyApplicationDescriptor)
    assert desc.id == "moex:implementation:moex-fibo-application:0.1"
    assert desc.conformance_level == "FIBO Extension Conformant"
    assert desc.namespace_iri == "https://data.moex.com/ontology/fibo-ext/"
    assert desc.external_source_id == "fibo"
    assert desc.missing_artifacts() == ()


def test_application_artifact_paths_exist() -> None:
    desc = load_ontology_application_descriptor(DESCRIPTOR)
    paths = desc.artifact_paths()
    assert paths["imported_module"].name == "fibo-import-module.ttl"
    assert paths["extension"].name == "moex-fibo-extension.ttl"
    assert paths["mapping"].name == "moex-dams-fibo-mapping.ttl"
    for path in paths.values():
        assert path.is_file(), path


def test_stub_ttls_parse_with_rdflib() -> None:
    desc = load_ontology_application_descriptor(DESCRIPTOR)
    for path in desc.artifact_paths().values():
        graph = Graph()
        graph.parse(path, format="turtle")
        assert len(graph) > 0, path


def test_missing_artifact_raises(tmp_path: Path) -> None:
    stub = tmp_path / "ontology-application.yaml"
    stub.write_text(
        "\n".join(
            [
                "id: moex:implementation:test:0.1",
                "namespace_iri: https://data.moex.com/ontology/test/",
                "conformance_level: FIBO Extension Conformant",
                "seed_ref: seeds/x.txt",
                "imported_module_ref: metamodel/missing.ttl",
                "extension_ref: metamodel/missing-ext.ttl",
                "mapping_ref: metamodel/missing-map.ttl",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError, match="artifacts missing"):
        load_ontology_application_descriptor(stub)


def test_public_export() -> None:
    assert PublicDescriptor is OntologyApplicationDescriptor
