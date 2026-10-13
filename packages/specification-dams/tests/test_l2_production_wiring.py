"""R2-1 / R3-2: L2 matrix validators must be reachable from production paths.

Gates:
1. Every L2-implemented ``dams_validator`` is listed in ``L2_PRODUCTION_CALLABLES``
   (exact dotted path — not merely a module allowlist).
2. Each listed callable is actually *invoked* from its production entry point
   (monkeypatched call counter).
3. ``default_dams_rule_sets`` invokes the assess-channel entry points.
4. Smoke: every ModelPackage-shaped manifest body passes L2-bearing
   assessments; primary solution packages pass full ``assess_implementation``.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import yaml
from moex_modeling import DiagnosticSeverity, ImplementationRef
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.application.repository import DamsAssetRepository
from moex_dams.application.rules_runner import (
    L2_PRODUCTION_CALLABLES,
    L2_PRODUCTION_MODULES,
    default_dams_rule_sets,
    run_rule_sets,
)
from moex_dams.rules.constraint_matrix import load_yaml, resolve_dams_validator

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
DAMS_SCHEMA = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)

# Assessments that host L2 matrix validators on the assess path.
# ``assessment:model-requirements`` is ADR-013 formal_checks (not L2 matrix).
L2_ASSESSMENT_IDS = frozenset(
    {
        "assessment:structural",
        "assessment:package-invariants",
        "assessment:catalog-topology",
        "assessment:governance-assignments",
    }
)

REQUIRED_ASSESSMENT_IDS = L2_ASSESSMENT_IDS | frozenset(
    {
        "assessment:model-requirements",
    }
)

# Entry drivers that must call the listed callables (always, on the fixture below).
# Values are zero-arg callables that exercise the production entry.
_MINIMAL_SEMANTIC = {
    "conceptual_properties": [
        {
            "element_id": "dams:prop/wire/probe",
            "name": "probe",
            "property_owner_entity_ref": "dams:concept/wire/probe",
            "significance_basis": ["business"],
        }
    ]
}


def _call(dotted_entry: str, *args: Any, **kwargs: Any) -> Any:
    """Call a production entry via its module attribute (sees monkeypatches)."""
    module_name, _, attr = dotted_entry.rpartition(".")
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)(*args, **kwargs)


def _drive_package_invariants() -> None:
    _call("moex_dams.rules.package_invariants.check_package_invariants", {})


def _drive_technical_assets() -> None:
    _call("moex_dams.rules.technical_assets.check_technical_assets", {})


def _drive_semantic_layer() -> None:
    _call("moex_dams.rules.semantic_layer.check_semantic_layer", _MINIMAL_SEMANTIC)


def _drive_conceptual() -> None:
    _call("moex_dams.rules.conceptual_entity.check_conceptual_entities", {})


def _drive_relation_terms() -> None:
    _call("moex_dams.rules.relation_terms.check_relation_terms", {})


def _drive_structural() -> None:
    _call("moex_dams.rules.structural.check_structural_data", {})


def _drive_catalog() -> None:
    _call("moex_dams.rules.catalog_topology.check_catalog_topology", {})


def _drive_governance() -> None:
    _call("moex_dams.rules.governance_assignments.check_governance_assignments", {})


def _drive_repository() -> None:
    _call(
        "moex_dams.rules.repository_invariants.check_repository_element_id_uniqueness",
        {"repository_id": "moex:repo:wire", "model_packages": []},
    )


def _drive_ontology() -> None:
    _call("moex_dams.rules.ontology_uris.check_ontology_uris", DAMS_SCHEMA)


# Map each production callable → driver that must invoke it.
_CALLABLE_DRIVERS: dict[str, Callable[[], None]] = {
    "moex_dams.rules.package_invariants.check_solution_scope_refs": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_attribute_cardinality_bounds": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_parent_concept_cycles": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_selection_attribute_closure": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_binding_compatibility": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_package_element_id_uniqueness": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_mapping_cardinality_consistency": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_relationship_endpoint_kinds": _drive_package_invariants,
    "moex_dams.rules.package_invariants.check_alignment_dual_path_consistency": _drive_package_invariants,
    "moex_dams.rules.catalog_topology.check_catalog_topology": _drive_catalog,
    "moex_dams.rules.governance_assignments.check_governance_assignments": _drive_governance,
    "moex_dams.rules.structural.check_structural_data": _drive_structural,
    "moex_dams.rules.conceptual_entity.check_conceptual_entities": _drive_conceptual,
    "moex_dams.rules.relation_terms.check_relation_terms": _drive_relation_terms,
    "moex_dams.rules.technical_assets.check_parent_ref_cycles": _drive_technical_assets,
    "moex_dams.rules.technical_assets.check_direction_forbidden": _drive_technical_assets,
    "moex_dams.rules.technical_assets.check_mapping_endpoint_types": _drive_technical_assets,
    "moex_dams.rules.technical_assets.check_operation_interface_ref": _drive_technical_assets,
    "moex_dams.rules.technical_assets.check_in_memory_location": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_source_pointer_requires_artifact": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_schema_dialect_format_family": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_node_kind_shape": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_reference_node_target": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_message_refs_kinds": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_node_edge_cycles": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_relational_slots": _drive_technical_assets,
    "moex_dams.rules.data_structure.check_local_key_unique": _drive_technical_assets,
    "moex_dams.rules.semantic_layer.check_identifying_requires_is_identifying": _drive_semantic_layer,
    "moex_dams.rules.ontology_uris.check_ontology_uris": _drive_ontology,
    "moex_dams.rules.repository_invariants.check_repository_element_id_uniqueness": _drive_repository,
}


def _l2_implemented_validators() -> list[tuple[str, str]]:
    data = load_yaml(MATRIX)
    out: list[tuple[str, str]] = []
    for inv in data.get("invariants") or []:
        ls = inv.get("level_status") or {}
        if str(ls.get("L2")) != "implemented":
            continue
        iid = str(inv.get("id") or "")
        dv = str((inv.get("implementation") or {}).get("dams_validator") or "")
        assert dv, f"{iid}: L2 implemented without dams_validator"
        out.append((iid, dv))
    return out


def test_default_rule_sets_register_l2_assessments(dams_schema: Path) -> None:
    ids = {
        s.assessment_id
        for s in default_dams_rule_sets(
            DamsAssetRepository(default_schema_path=dams_schema)
        )
    }
    missing = REQUIRED_ASSESSMENT_IDS - ids
    assert not missing, f"missing L2 assessments in default_dams_rule_sets: {sorted(missing)}"


def test_every_l2_implemented_validator_is_listed_as_production_callable() -> None:
    missing: list[str] = []
    for iid, dv in _l2_implemented_validators():
        resolve_dams_validator(dv)  # must import
        if dv not in L2_PRODUCTION_CALLABLES:
            missing.append(f"{iid}: {dv}")
        module = dv.rsplit(".", 1)[0]
        assert module in L2_PRODUCTION_MODULES, (
            f"{iid}: module {module} missing from L2_PRODUCTION_MODULES"
        )
    assert not missing, (
        "L2-implemented dams_validator not in L2_PRODUCTION_CALLABLES "
        "(add exact dotted path + a driver in test_l2_production_wiring):\n"
        + "\n".join(missing)
    )


def test_production_callables_cover_only_matrix_validators() -> None:
    """No stale entries in L2_PRODUCTION_CALLABLES beyond the matrix."""
    matrix_dvs = {dv for _, dv in _l2_implemented_validators()}
    stale = sorted(L2_PRODUCTION_CALLABLES - matrix_dvs)
    assert not stale, (
        "L2_PRODUCTION_CALLABLES has paths not used by any L2-implemented INV:\n"
        + "\n".join(stale)
    )


def test_every_production_callable_is_invoked_by_its_driver(monkeypatch: Any) -> None:
    """Each callable must be called when its production entry runs (not just listed)."""
    assert set(_CALLABLE_DRIVERS) == set(L2_PRODUCTION_CALLABLES), (
        "Driver map must match L2_PRODUCTION_CALLABLES exactly. "
        f"missing drivers={sorted(L2_PRODUCTION_CALLABLES - set(_CALLABLE_DRIVERS))}; "
        f"extra drivers={sorted(set(_CALLABLE_DRIVERS) - L2_PRODUCTION_CALLABLES)}"
    )

    # Group callables by driver identity so we wrap once per entry and assert all.
    by_driver: dict[Callable[[], None], list[str]] = {}
    for dotted, driver in _CALLABLE_DRIVERS.items():
        by_driver.setdefault(driver, []).append(dotted)

    for driver, dotted_list in by_driver.items():
        counters: dict[str, int] = {d: 0 for d in dotted_list}
        originals: dict[str, Any] = {}
        for dotted in dotted_list:
            module_name, _, attr = dotted.rpartition(".")
            import importlib

            mod = importlib.import_module(module_name)
            originals[dotted] = getattr(mod, attr)

            def _make_wrapper(path: str, orig: Any) -> Any:
                def _wrapped(*args: Any, **kwargs: Any) -> Any:
                    counters[path] += 1
                    return orig(*args, **kwargs)

                return _wrapped

            monkeypatch.setattr(
                mod, attr, _make_wrapper(dotted, originals[dotted]), raising=True
            )

        driver()

        not_called = [d for d, n in counters.items() if n < 1]
        assert not not_called, (
            f"driver {driver.__name__} did not invoke: {not_called}"
        )


def test_default_rule_sets_invoke_assess_l2_entries(
    dams_schema: Path, monkeypatch: Any
) -> None:
    """``run_rule_sets`` must call the assess-channel entry validators."""
    import moex_dams.application.rules_runner as rr
    from moex_dams.rules import structural as struct_mod

    hits = {
        "check_package_invariants": 0,
        "check_catalog_topology": 0,
        "check_governance_assignments": 0,
        "check_structural_data": 0,
        "check_formal_requirements_for_repo": 0,
    }

    def _wrap(name: str, orig: Any) -> Any:
        def _inner(*args: Any, **kwargs: Any) -> Any:
            hits[name] += 1
            return orig(*args, **kwargs)

        return _inner

    # Closures in rules_runner look up these names in rr's globals at call time.
    monkeypatch.setattr(
        rr,
        "check_package_invariants",
        _wrap("check_package_invariants", rr.check_package_invariants),
    )
    monkeypatch.setattr(
        rr,
        "check_catalog_topology",
        _wrap("check_catalog_topology", rr.check_catalog_topology),
    )
    monkeypatch.setattr(
        rr,
        "check_governance_assignments",
        _wrap("check_governance_assignments", rr.check_governance_assignments),
    )
    # check_structural → check_structural_data via structural module globals.
    monkeypatch.setattr(
        struct_mod,
        "check_structural_data",
        _wrap("check_structural_data", struct_mod.check_structural_data),
    )
    # formal_checks is bound into RuleSet at construction — patch before rebuild.
    monkeypatch.setattr(
        rr,
        "check_formal_requirements_for_repo",
        _wrap(
            "check_formal_requirements_for_repo",
            rr.check_formal_requirements_for_repo,
        ),
    )

    repo = DamsAssetRepository(default_schema_path=dams_schema)
    sets = rr.default_dams_rule_sets(repo)
    body = LinkMLImplementationBody(
        source_path=str(REPO_ROOT / "model-assets" / "implementations" / "wire.yaml"),
        target_class="ModelPackage",
        data={"element_id": "dams:model/wire", "name": "wire"},
    )
    run_rule_sets(body, sets)

    missing = [k for k, n in hits.items() if n < 1]
    assert not missing, f"default_dams_rule_sets did not invoke: {missing}"


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


def _is_model_package_body(data: dict[str, Any]) -> bool:
    if data.get("namespace_iri") or data.get("seed_ref"):
        return False
    return bool(data.get("element_id") or data.get("logical_entities"))


def test_all_manifest_model_packages_pass_l2_assessments(
    dams_schema: Path,
) -> None:
    """Smoke: every ModelPackage body runs L2-bearing assessments without ERROR.

    Excludes ``assessment:standard-syntax`` (LinkML shape debt on hierarchy/draft)
    and ``assessment:model-requirements`` (ADR-013 formal_checks; drafts / esed
    still carry known REQ gaps). L2 matrix paths must stay clean everywhere.
    """
    assert MANIFEST.is_file()
    doc = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    docs = doc.get("documents") or []
    assert docs, "manifest has no documents"

    repo = DamsAssetRepository(default_schema_path=dams_schema)
    sets = tuple(
        s
        for s in default_dams_rule_sets(repo)
        if s.assessment_id in L2_ASSESSMENT_IDS
    )
    assert {s.assessment_id for s in sets} == L2_ASSESSMENT_IDS

    packages: list[tuple[str, Path]] = []
    for entry in docs:
        if not isinstance(entry, dict) or str(entry.get("kind") or "") != "package":
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
        data = body.data if isinstance(body.data, dict) else {}
        if _is_model_package_body(data):
            packages.append((impl_id, body_path))

    assert len(packages) >= 7, (
        f"expected >=7 ModelPackage bodies in manifest, got {len(packages)}: "
        f"{[p[0] for p in packages]}"
    )

    errors: list[str] = []
    for impl_id, body_path in packages:
        body = repo.load_implementation(
            ImplementationRef(
                implementation_id=impl_id,
                implementation_revision="1",
            ),
            path=body_path,
        )
        for rule_set, diags in run_rule_sets(body, sets):
            for d in diags:
                if d.severity is not DiagnosticSeverity.ERROR:
                    continue
                errors.append(
                    f"{body_path.relative_to(REPO_ROOT)} "
                    f"[{rule_set.assessment_id}] {d.diagnostic_code}: "
                    f"{d.diagnostic_message}"
                )

    assert not errors, "L2-assessment ERROR diagnostics:\n" + "\n".join(errors)


def test_primary_solution_packages_assess_conformant(
    dams_schema: Path,
) -> None:
    """Full ``assess_implementation`` on primary green solution packages.

    esed still has known REQ-ATR/PDM gaps; enterprise fails LinkML validate —
    both are covered by the L2-assessment smoke above, not this gate.
    """
    from moex_dams import assess_implementation
    from moex_modeling import ConformanceResult

    targets = [
        (
            "moex:implementation:mdm:0.1.0",
            REPO_ROOT
            / "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml",
        ),
        (
            "moex:implementation:crm:0.1.0",
            REPO_ROOT
            / "model-assets/implementations/solutions/crm/crm-solution-model.yaml",
        ),
        (
            "moex:implementation:ucd:0.1.0",
            REPO_ROOT
            / "model-assets/implementations/solutions/ucd/ucd-solution-model.yaml",
        ),
    ]
    ok = {
        ConformanceResult.CONFORMANT,
        ConformanceResult.CONFORMANT_WITH_WARNINGS,
    }
    failures: list[str] = []
    for impl_id, path in targets:
        assert path.is_file(), path
        result = assess_implementation(
            schema_path=dams_schema,
            implementation_path=path,
            implementation_id=impl_id,
        )
        if result.report.overall_result not in ok:
            err_codes = [
                f"{a.id}:{d.diagnostic_code}"
                for a in result.report.assessments
                for d in a.diagnostics
                if d.severity is DiagnosticSeverity.ERROR
            ]
            failures.append(
                f"{impl_id}: {result.report.overall_result} "
                f"(errors={err_codes[:8]})"
            )
    assert not failures, "assess_implementation failures:\n" + "\n".join(failures)
