"""pySHACL fixtures for RDF instances of ModelPackage (Stage 8 / ADR-030)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pyshacl = pytest.importorskip("pyshacl")
from linkml_runtime import SchemaView  # noqa: E402
from linkml_runtime.dumpers.rdflib_dumper import RDFLibDumper  # noqa: E402
from linkml_runtime.loaders import yaml_loader  # noqa: E402
from pyshacl import validate  # noqa: E402
from rdflib import Namespace  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
SHACL = (
    REPO_ROOT / "generated" / "artifacts" / "moex-dams" / "0.1" / "moex-dams.shacl.ttl"
)
VALID = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "ontology"
    / "valid-model-package.yaml"
)
DAMS = Namespace("https://data.moex.com/dams/")

sys.path.insert(0, str(REPO_ROOT / "generated" / "artifacts" / "moex-dams" / "0.1" / "python"))
from moex_dams import ModelPackage  # noqa: E402


def _dump_valid():
    sv = SchemaView(str(SCHEMA))
    obj = yaml_loader.load(str(VALID), target_class=ModelPackage)
    return RDFLibDumper().as_rdf_graph(obj, schemaview=sv)


def test_valid_model_package_conforms_to_shacl() -> None:
    assert SHACL.is_file()
    g = _dump_valid()
    conforms, _report_g, report_text = validate(
        data_graph=g,
        shacl_graph=SHACL.read_text(encoding="utf-8"),
        inference="none",
        abort_on_first=False,
    )
    assert conforms, report_text


def test_missing_lifecycle_status_fails_shacl() -> None:
    g = _dump_valid()
    # Remove required datatype property to force a shape violation.
    for triple in list(g.triples((None, DAMS.lifecycle_status, None))):
        g.remove(triple)
    conforms, _report_g, report_text = validate(
        data_graph=g,
        shacl_graph=SHACL.read_text(encoding="utf-8"),
        inference="none",
        abort_on_first=False,
    )
    assert not conforms, "expected SHACL failure after removing lifecycle_status"
    assert report_text
