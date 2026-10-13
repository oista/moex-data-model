"""R2-1: L2 matrix validators must be reachable from production assess path."""

from __future__ import annotations

from pathlib import Path

import yaml
from moex_modeling import DiagnosticSeverity, ImplementationRef

from moex_dams.application.repository import DamsAssetRepository
from moex_dams.application.rules_runner import (
    L2_PRODUCTION_MODULES,
    default_dams_rule_sets,
    run_rule_sets,
)
from moex_dams.rules.constraint_matrix import load_yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MATRIX = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "constraints"
    / "constraint-matrix.yaml"
)
MANIFEST = REPO_ROOT / "model-assets" / "implementations" / "manifest.yaml"

REQUIRED_ASSESSMENT_IDS = frozenset(
    {
        "assessment:structural",
        "assessment:package-invariants",
        "assessment:catalog-topology",
        "assessment:governance-assignments",
        "assessment:model-requirements",
    }
)


def test_default_rule_sets_register_l2_assessments(dams_schema: Path) -> None:
    ids = {
        s.assessment_id
        for s in default_dams_rule_sets(
            DamsAssetRepository(default_schema_path=dams_schema)
        )
    }
    missing = REQUIRED_ASSESSMENT_IDS - ids
    assert not missing, f"missing L2 assessments in default_dams_rule_sets: {sorted(missing)}"


def test_every_l2_implemented_validator_module_is_production_wired() -> None:
    data = load_yaml(MATRIX)
    missing: list[str] = []
    for inv in data.get("invariants") or []:
        ls = inv.get("level_status") or {}
        if str(ls.get("L2")) != "implemented":
            continue
        dv = str((inv.get("implementation") or {}).get("dams_validator") or "")
        assert dv, f"{inv.get('id')}: L2 implemented without dams_validator"
        module = dv.rsplit(".", 1)[0]
        if module not in L2_PRODUCTION_MODULES:
            missing.append(f"{inv.get('id')}: {dv} (module {module})")
    assert not missing, (
        "L2-implemented validators not listed in L2_PRODUCTION_MODULES "
        "(wire into default_dams_rule_sets / formal_checks / schema lint):\n"
        + "\n".join(missing)
    )


def _resolve_package_body(envelope_yaml: Path) -> tuple[str, Path] | None:
    """Return (implementation_id, body_path) for an implementation.yaml envelope."""
    impl = yaml.safe_load(envelope_yaml.read_text(encoding="utf-8")) or {}
    if not isinstance(impl, dict):
        return None
    body_ref = impl.get("body_ref")
    if not body_ref:
        return None
    body_path = (envelope_yaml.parent / str(body_ref)).resolve()
    if not body_path.is_file():
        return None
    impl_id = str(impl.get("id") or envelope_yaml.parent.name)
    return impl_id, body_path


def test_manifest_packages_pass_new_l2_rule_sets(dams_schema: Path) -> None:
    """Smoke: all ModelPackage-shaped manifest bodies run new L2 sets without ERROR."""
    assert MANIFEST.is_file()
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    docs = doc.get("documents") or []
    assert docs, "manifest has no documents"

    repo = DamsAssetRepository(default_schema_path=dams_schema)
    sets = tuple(
        s
        for s in default_dams_rule_sets(repo)
        if s.assessment_id
        in {
            "assessment:package-invariants",
            "assessment:catalog-topology",
            "assessment:governance-assignments",
        }
    )
    assert len(sets) == 3

    errors: list[str] = []
    checked = 0
    for entry in docs:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("kind") or "") != "package":
            continue
        rel = entry.get("path")
        if not rel:
            continue
        envelope = (MANIFEST.parent / str(rel)).resolve()
        if not envelope.is_file():
            continue
        resolved = _resolve_package_body(envelope)
        if resolved is None:
            continue
        impl_id, body_path = resolved
        body = repo.load_implementation(
            ImplementationRef(
                implementation_id=impl_id,
                implementation_revision="1",
            ),
            path=body_path,
        )
        # Ontology application bodies are not ModelPackage-shaped; skip quietly.
        data = body.data if isinstance(body.data, dict) else {}
        if not data.get("element_id") and not data.get("logical_entities"):
            if data.get("namespace_iri") or data.get("seed_ref"):
                continue
        checked += 1
        for rule_set, diags in run_rule_sets(body, sets):
            for d in diags:
                if d.severity is not DiagnosticSeverity.ERROR:
                    continue
                errors.append(
                    f"{body_path.relative_to(REPO_ROOT)} "
                    f"[{rule_set.assessment_id}] {d.diagnostic_code}: "
                    f"{d.diagnostic_message}"
                )

    assert checked >= 6, f"expected >=6 ModelPackage bodies, got {checked}"
    assert not errors, "L2 ERROR diagnostics on manifest packages:\n" + "\n".join(
        errors
    )
