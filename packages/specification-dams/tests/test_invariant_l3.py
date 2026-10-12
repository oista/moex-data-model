"""PR-C4b: manual SHACL forms with sh:sourceShape → INV-NNN + differential L1/L2/L3."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pyshacl = pytest.importorskip("pyshacl")
from pyshacl import validate  # noqa: E402
from rdflib import Graph, Namespace, URIRef  # noqa: E402

from moex_dams.rules.constraint_matrix import (
    _collect_invariant_ids,
    _run_l2_package_checks,
    load_yaml,
    repo_root,
)
from moex_standard_linkml.validation import error_results, make_linkml_validator

DAMS = Namespace("https://data.moex.com/dams/")
REPO = repo_root()
MANUAL = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "constraints"
    / "shacl"
    / "manual"
    / "invariants.ttl"
)
L3 = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "invariants"
    / "l3"
)
L1_DIR = L3.parent
L2_DIR = L1_DIR / "l2"
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
MANIFEST = L1_DIR / "manifest.yaml"

L3_IDS = [f"INV-{i:03d}" for i in range(1, 18)]


def _violating_source_shapes(report_graph: Graph) -> set[str]:
    """Return INV-NNN ids referenced via sh:sourceShape on failing results."""
    sh = Namespace("http://www.w3.org/ns/shacl#")
    out: set[str] = set()
    for result in report_graph.subjects(URIRef(str(sh) + "resultSeverity"), None):
        # Walk result → sourceShape (direct or via resultPath chain)
        for shape in report_graph.objects(result, sh.sourceShape):
            local = str(shape).rsplit("/", 1)[-1]
            if local.startswith("INV-"):
                out.add(local)
        for source in report_graph.objects(result, sh.sourceConstraintComponent):
            _ = source
    # Also scan messages / focus nodes' shapes from validation report text fallback
    for shape in report_graph.objects(None, sh.sourceShape):
        local = str(shape).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        if local.startswith("INV-"):
            out.add(local)
    return out


def _l3_conforms(path: Path) -> tuple[bool, Graph, str]:
    data = Graph().parse(path, format="turtle")
    shapes = Graph().parse(MANUAL, format="turtle")
    conforms, report_g, report_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        inference="none",
        abort_on_first=False,
    )
    return conforms, report_g, report_text


@pytest.mark.parametrize("iid", L3_IDS)
def test_l3_fixtures_source_shape(iid: str) -> None:
    assert MANUAL.is_file()
    valid = L3 / f"{iid}.valid.ttl"
    invalid = L3 / f"{iid}.invalid.ttl"
    assert valid.is_file() and invalid.is_file()

    ok, _, text = _l3_conforms(valid)
    assert ok, f"{iid} valid must conform: {text}"

    bad, report_g, text = _l3_conforms(invalid)
    assert not bad, f"{iid} invalid must fail"
    shapes = _violating_source_shapes(report_g)
    # Prefer sourceShape attribution; fall back to message containing INV id
    if iid not in shapes and iid not in text:
        pytest.fail(f"{iid}: expected sourceShape/message; shapes={shapes} text={text[:400]}")


def test_shacl_generator_does_not_emit_inv_rules() -> None:
    """gen-shacl output must not contain INV-NNN from LinkML rule descriptions."""
    import os
    import sys

    from linkml.generators.shaclgen import ShaclGenerator

    sys.path.insert(0, str(REPO / "scripts"))
    from generate_artifacts import SHACL_OPTIONS

    schema = SCHEMA
    cwd = os.getcwd()
    try:
        os.chdir(schema.parent)
        text = ShaclGenerator(schema.name, **SHACL_OPTIONS).serialize()
    finally:
        os.chdir(cwd)
    for i in range(1, 18):
        assert f"INV-{i:03d}" not in text


def test_differential_l1_l3_agree_on_inv002() -> None:
    """Spot-check: INV-002 valid/invalid agree across L1 JSON Schema and L3 SHACL."""
    iid = "INV-002"
    man = load_yaml(MANIFEST)
    case = next(c for c in man["cases"] if c["id"] == iid)
    validator = make_linkml_validator(SCHEMA)
    target = case["target_class"]
    l1_valid = yaml.safe_load((L1_DIR / case["valid"]).read_text(encoding="utf-8"))
    l1_invalid = yaml.safe_load((L1_DIR / case["invalid"]).read_text(encoding="utf-8"))
    l1_ok = error_results(validator.validate(l1_valid, target_class=target)) == []
    l1_bad = bool(error_results(validator.validate(l1_invalid, target_class=target)))
    ok_v, _, _ = _l3_conforms(L3 / f"{iid}.valid.ttl")
    ok_i, _, _ = _l3_conforms(L3 / f"{iid}.invalid.ttl")
    assert l1_ok == ok_v
    assert l1_bad == (not ok_i)


def test_differential_l2_l3_agree_on_inv010() -> None:
    """Spot-check: INV-010 L2 package fixtures agree with L3 SHACL verdicts."""
    iid = "INV-010"
    l2v = yaml.safe_load((L2_DIR / f"{iid}.valid.yaml").read_text(encoding="utf-8"))
    l2i = yaml.safe_load((L2_DIR / f"{iid}.invalid.yaml").read_text(encoding="utf-8"))
    l2_ok = iid not in _collect_invariant_ids(_run_l2_package_checks(l2v))
    l2_bad = iid in _collect_invariant_ids(_run_l2_package_checks(l2i))
    ok_v, _, _ = _l3_conforms(L3 / f"{iid}.valid.ttl")
    ok_i, _, _ = _l3_conforms(L3 / f"{iid}.invalid.ttl")
    assert l2_ok == ok_v
    assert l2_bad == (not ok_i)
