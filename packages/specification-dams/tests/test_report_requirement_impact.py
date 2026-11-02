"""Guards for scripts/report_requirement_impact.py (ADR-056 PR-11a)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from report_requirement_impact import (  # noqa: E402
    _count_file,
    _details_map,
    _iter_targets,
)

EXAMPLE = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples"
    / "it-solution-model.example.yaml"
)


def test_details_map_reads_diagnostic_details() -> None:
    from moex_modeling.conformance.domain import Diagnostic
    from moex_modeling.shared.enums import DiagnosticSeverity
    from moex_modeling.shared.types import DiagnosticDetail

    diag = Diagnostic(
        diagnostic_code="DAMS-REQ-PDM-004.c1",
        severity=DiagnosticSeverity.ERROR,
        diagnostic_message="needs field_mapping",
        diagnostic_details=(
            DiagnosticDetail(detail_key="requirement_code", detail_value="PDM-02"),
        ),
    )
    assert _details_map(diag)["requirement_code"] == "PDM-02"


def test_details_map_falls_back_to_details_attr() -> None:
    detail = types.SimpleNamespace(detail_key="requirement_code", detail_value="LDM-01")
    diag = types.SimpleNamespace(details=(detail,))
    assert _details_map(diag)["requirement_code"] == "LDM-01"


def test_iter_targets_finds_four_solutions_and_enterprise() -> None:
    paths = _iter_targets(REPO_ROOT)
    names = {p.name for p in paths}
    assert "enterprise-conceptual-model.yaml" in names
    solutions = [p for p in paths if p.name.endswith("-solution-model.yaml")]
    assert len(solutions) == 4


def test_count_file_keys_requirement_code_pdm02(tmp_path: Path) -> None:
    """Stripped example must report PDM-02 under requirement_code, not '-'."""
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    # Remove field_mappings so PDM-02.c2 fires (same as formal_checks ATR-005 case).
    data.pop("field_mappings", None)
    for attr in data.get("logical_entities", [{}])[0].get("attributes", []):
        if isinstance(attr, dict):
            attr.pop("mapping_coverage_status", None)
            attr.pop("mapping_rationale", None)
    path = tmp_path / "fixture-solution-model.yaml"
    path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")

    counts = _count_file(path, repo_root=REPO_ROOT)
    pdm02 = [k for k in counts if k[0] == "PDM-02" and k[1] == "DAMS-REQ-PDM-004.c1"]
    assert pdm02, f"expected ('PDM-02', 'DAMS-REQ-PDM-004.c1', ...), got {sorted(counts)}"
    assert all(k[0] != "-" for k in counts if k[1].startswith("DAMS-REQ-"))
