"""Validate constraint-matrix.yaml against its schema and structural rules (ADR-045).

PR-C3a: logic lives in this package; ``scripts/check_constraint_matrix.py`` is a CLI wrapper.
PR-C3b: level_status, INV-prefix check, L1/L2 fixture runners.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml

INV_PREFIX_RE = re.compile(r"^(INV-\d{3}):")

# Former diagnostic_code values kept as aliases (requirement_code / docs).
DIAGNOSTIC_CODE_ALIASES: dict[str, frozenset[str]] = {
    "INV-012": frozenset({"DAMS-REQ-PDM-020.c1", "DAMS-REQ-PDM-020.c2"}),
    "INV-013": frozenset({"DAMS-REQ-PDM-020.c3", "DAMS-REQ-PDM-020.c4"}),
    "INV-015": frozenset({"DAMS-REQ-PDM-012.c1"}),
    "INV-016": frozenset({"DAMS-REQ-PDM-011.c1"}),
    "INV-017": frozenset({"DAMS-REQ-PDM-018.c1"}),
    "INV-018": frozenset({"DAMS-REQ-PDM-008.c1"}),
    "INV-019": frozenset({"DAMS-REQ-PDM-018.c2"}),
    "INV-020": frozenset({"DAMS-REQ-PDM-014.c1"}),
    "INV-021": frozenset({"DAMS-REQ-PDM-016.c1"}),
    "INV-022": frozenset({"DAMS-REQ-PDM-013.c1"}),
    "INV-026": frozenset({"MOEX-ONT-004"}),
    "INV-033": frozenset({"DAMS-REQ-PDM-009.c1"}),
    "INV-034": frozenset({"DAMS-REQ-PDM-009.c2"}),
}


def canonical_diagnostic_code(inv_id: str) -> str:
    """Canonical L2/L3 tagged code: DAMS-INV-NNN."""
    return f"DAMS-{inv_id}"


def resolve_dams_validator(dotted: str) -> Any:
    """Import ``package.module.callable`` and return the attribute."""
    import importlib

    dotted = str(dotted).strip()
    if not dotted or "." not in dotted:
        raise ValueError(f"dams_validator must be a dotted callable path, got {dotted!r}")
    module_name, _, attr = dotted.rpartition(".")
    module = importlib.import_module(module_name)
    obj = getattr(module, attr, None)
    if obj is None:
        raise ValueError(f"dams_validator {dotted!r}: attribute missing")
    if not callable(obj):
        raise ValueError(f"dams_validator {dotted!r}: not callable")
    return obj


def repo_root() -> Path:
    """Return repository root (…/moex-data-model)."""
    return Path(__file__).resolve().parents[5]


def matrix_path(root: Path | None = None) -> Path:
    root = root or repo_root()
    return (
        root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "constraints"
        / "constraint-matrix.yaml"
    )


def schema_path(root: Path | None = None) -> Path:
    return matrix_path(root).with_name("constraint-matrix.schema.yaml")


def schema_dir(root: Path | None = None) -> Path:
    root = root or repo_root()
    return root / "model-assets" / "specifications" / "moex-dams" / "0.1" / "schemas"


def dams_schema_path(root: Path | None = None) -> Path:
    return schema_dir(root) / "moex-dams.yaml"


def doc_out_path(root: Path | None = None) -> Path:
    root = root or repo_root()
    return root / "docs" / "architecture" / "constraint-matrix.md"


def invariants_dir(root: Path | None = None) -> Path:
    root = root or repo_root()
    return (
        root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
        / "invariants"
    )


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def list_schema_rules_detailed(
    root: Path | None = None,
) -> list[tuple[str, str, int, str]]:
    """Return (schema_file, class_name, rule_index, description)."""
    root = root or repo_root()
    out: list[tuple[str, str, int, str]] = []
    for path in sorted(schema_dir(root).glob("*.yaml")):
        data = load_yaml(path) or {}
        for cname, body in (data.get("classes") or {}).items():
            for idx, rule in enumerate((body or {}).get("rules") or []):
                desc = str((rule or {}).get("description") or "")
                out.append((path.name, cname, idx, desc))
    return out


def list_schema_rules(root: Path | None = None) -> list[tuple[str, str, int]]:
    return [(f, c, i) for f, c, i, _ in list_schema_rules_detailed(root)]


def canon_rules(rules: list[tuple[str, str, int]]) -> str:
    return "\n".join(f"{f}|{c}|{i}" for f, c, i in rules) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_overall_status(levels: list[str], level_status: dict[str, str]) -> str:
    """Aggregate level_status → overall status (ignores waived / not-applicable)."""
    active: list[str] = []
    for level in levels:
        status = str(level_status.get(level) or "")
        if status in ("", "not-applicable", "waived"):
            continue
        active.append(status)
    if levels and all(
        str(level_status.get(level) or "") in ("waived", "not-applicable")
        for level in levels
    ):
        return "waived"
    if not active:
        return "planned"
    if all(status == "implemented" for status in active):
        return "implemented"
    if all(status == "planned" for status in active):
        return "planned"
    return "implemented-untested"


def _is_data_fixture(path: str) -> bool:
    return path.endswith((".yaml", ".yml")) and not path.endswith(".py")


def _error_messages(report: Any) -> list[str]:
    from moex_standard_linkml.validation import error_results

    out: list[str] = []
    for item in error_results(report):
        out.append(str(getattr(item, "message", item)))
    return out


def _run_l1_fixtures(
    inv: dict[str, Any], *, root: Path, errors: list[str]
) -> None:
    """Valid must pass; invalid must fail. Attribute via INV in rule description + class."""
    from moex_standard_linkml.validation import make_linkml_validator

    iid = str(inv.get("id"))
    tests = inv.get("tests") or {}
    valid_paths = [p for p in (tests.get("l1_valid") or []) if _is_data_fixture(str(p))]
    invalid_paths = [
        p for p in (tests.get("l1_invalid") or []) if _is_data_fixture(str(p))
    ]
    if not valid_paths or not invalid_paths:
        errors.append(f"{iid}: L1 implemented requires l1_valid and l1_invalid YAML")
        return

    lr = ((inv.get("implementation") or {}).get("linkml_rule")) or {}
    target = str(lr.get("class_name") or "")
    if not target:
        errors.append(f"{iid}: L1 implemented requires implementation.linkml_rule.class_name")
        return

    # Confirm schema rule description carries this INV id.
    detailed = list_schema_rules_detailed(root)
    match = [
        d
        for d in detailed
        if d[0] == lr.get("schema_file")
        and d[1] == lr.get("class_name")
        and d[2] == int(lr.get("rule_index", -1))
    ]
    if not match:
        errors.append(f"{iid}: linkml_rule not found in schemas for L1 run")
        return
    desc = match[0][3]
    m = INV_PREFIX_RE.match(desc.strip())
    if not m or m.group(1) != iid:
        errors.append(
            f"{iid}: L1 rule description must start with '{iid}:', got {desc!r}"
        )
        return

    validator = make_linkml_validator(dams_schema_path(root))
    for vp in valid_paths:
        path = root / str(vp)
        if not path.is_file():
            errors.append(f"{iid}: missing L1 valid fixture {vp}")
            continue
        data = load_yaml(path)
        msgs = _error_messages(validator.validate(data, target_class=target))
        if msgs:
            errors.append(f"{iid}: L1 valid fixture must pass: {vp}: {msgs[0]}")

    for ip in invalid_paths:
        path = root / str(ip)
        if not path.is_file():
            errors.append(f"{iid}: missing L1 invalid fixture {ip}")
            continue
        data = load_yaml(path)
        msgs = _error_messages(validator.validate(data, target_class=target))
        if not msgs:
            errors.append(f"{iid}: L1 invalid fixture must fail: {ip}")
            continue
        joined = " ".join(msgs)
        expected = None
        man_path = invariants_dir(root) / "manifest.yaml"
        if man_path.is_file():
            man = load_yaml(man_path) or {}
            for case in man.get("cases") or []:
                if case.get("id") == iid:
                    expected = case.get("expected_error")
                    break
        if not expected:
            errors.append(
                f"{iid}: L1 invalid requires expected_error in "
                f"examples/invariants/manifest.yaml (got rejection: {msgs[0]!r})"
            )
        elif str(expected) not in joined and iid not in joined:
            errors.append(
                f"{iid}: L1 invalid error must contain expected_error={expected!r} "
                f"or {iid}; got {msgs[0]!r}"
            )


def _collect_invariant_ids(diags: list[Any]) -> set[str]:
    out: set[str] = set()
    for d in diags:
        for det in getattr(d, "diagnostic_details", None) or ():
            if getattr(det, "detail_key", None) == "invariant_id":
                out.add(str(det.detail_value))
        code = str(getattr(d, "diagnostic_code", "") or "")
        if code.startswith("DAMS-INV-"):
            out.add(code.replace("DAMS-", ""))
    return out


def _run_l2_package_checks(data: dict[str, Any]) -> list[Any]:
    """Run L2 package checks once (technical_assets already includes data_structures)."""
    from moex_dams.rules.semantic_layer import check_semantic_layer
    from moex_dams.rules.technical_assets import check_technical_assets

    diags: list[Any] = []
    diags.extend(check_semantic_layer(data))
    diags.extend(check_technical_assets(data))
    return diags


def _diag_matches_inv(diag: Any, iid: str) -> bool:
    for det in getattr(diag, "diagnostic_details", None) or ():
        if getattr(det, "detail_key", None) == "invariant_id":
            if str(det.detail_value) == iid:
                return True
    code = str(getattr(diag, "diagnostic_code", "") or "")
    if code == canonical_diagnostic_code(iid):
        return True
    if code.startswith("DAMS-INV-") and code.replace("DAMS-", "") == iid:
        return True
    return False


def _severity_value(diag: Any) -> str:
    sev = getattr(diag, "severity", None)
    if sev is None:
        return ""
    return str(getattr(sev, "value", sev)).lower()


def _run_l2_fixtures(
    inv: dict[str, Any], *, root: Path, errors: list[str]
) -> None:
    iid = str(inv.get("id"))
    expected_code = canonical_diagnostic_code(iid)
    expected_sev = str(inv.get("severity") or "error").lower()
    tests = inv.get("tests") or {}
    valid_paths = [p for p in (tests.get("l2_valid") or []) if _is_data_fixture(str(p))]
    invalid_paths = [
        p for p in (tests.get("l2_invalid") or []) if _is_data_fixture(str(p))
    ]
    if not valid_paths or not invalid_paths:
        errors.append(
            f"{iid}: L2 implemented requires l2_valid and l2_invalid YAML fixtures "
            "(not .py unit-test paths)"
        )
        return

    for vp in valid_paths:
        path = root / str(vp)
        if not path.is_file():
            errors.append(f"{iid}: missing L2 valid fixture {vp}")
            continue
        data = load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{iid}: L2 valid fixture must be a mapping: {vp}")
            continue
        ids = _collect_invariant_ids(_run_l2_package_checks(data))
        if iid in ids:
            errors.append(f"{iid}: L2 valid fixture must not emit {iid}: {vp}")

    for ip in invalid_paths:
        path = root / str(ip)
        if not path.is_file():
            errors.append(f"{iid}: missing L2 invalid fixture {ip}")
            continue
        if iid == "INV-026":
            from moex_dams.rules.ontology_uris import check_ontology_uris

            diags = list(check_ontology_uris(path))
        else:
            data = load_yaml(path)
            if not isinstance(data, dict):
                errors.append(f"{iid}: L2 invalid fixture must be a mapping: {ip}")
                continue
            diags = _run_l2_package_checks(data)
        matched = [d for d in diags if _diag_matches_inv(d, iid)]
        if not matched:
            errors.append(
                f"{iid}: L2 invalid fixture must emit invariant_id={iid}: {ip}"
            )
            continue
        codes = {str(getattr(d, "diagnostic_code", "") or "") for d in matched}
        if expected_code not in codes and not (codes & DIAGNOSTIC_CODE_ALIASES.get(iid, frozenset())):
            errors.append(
                f"{iid}: L2 invalid must emit diagnostic_code={expected_code} "
                f"(or documented alias); got {sorted(codes)}: {ip}"
            )
        severities = {_severity_value(d) for d in matched}
        if expected_sev not in severities:
            errors.append(
                f"{iid}: L2 invalid severity must include {expected_sev!r}; "
                f"got {sorted(severities)}: {ip}"
            )


def validate_matrix(
    data: dict[str, Any],
    *,
    root: Path | None = None,
    run_fixtures: bool = True,
    gate_strict: bool = False,
) -> list[str]:
    """Return structural (and optional fixture-runner) errors for the matrix.

    ``gate_strict`` (PR-C5 / publish-gate): reject ``planned`` and
    ``implemented-untested`` overall statuses.
    """
    root = root or repo_root()
    errors: list[str] = []

    from moex_standard_linkml.validation import error_results, make_linkml_validator

    report = make_linkml_validator(schema_path(root)).validate(
        data, target_class="ConstraintMatrix"
    )
    for item in error_results(report):
        errors.append(f"schema: {getattr(item, 'message', item)}")

    invs = list(data.get("invariants") or [])
    by_id = {str(inv.get("id")): inv for inv in invs}
    if len(by_id) != len(invs):
        errors.append("duplicate invariant id")

    registry = [str(x) for x in (data.get("invariant_id_registry") or [])]
    if not registry:
        errors.append("missing invariant_id_registry (append-only INV-ID list)")
    else:
        for iid in by_id:
            if iid not in registry:
                errors.append(
                    f"{iid}: present in invariants but missing from invariant_id_registry"
                )
        # Append-only: registry may contain retired ids not in invariants, but
        # every registry id that is not in invariants must be documented later;
        # for now require registry == sorted(active ids) or registry ⊇ active.
        extra = [iid for iid in registry if iid not in by_id]
        if extra:
            # Allowed only if those ids were waived/retired with adr — soft for C5:
            # require no silent drop: active must be subset (already checked).
            pass
        for iid in registry:
            if not INV_PREFIX_RE.match(iid + ":"):
                errors.append(f"invariant_id_registry entry malformed: {iid!r}")

    # Optional legacy baseline (PR-C1..C4); ignored when absent (PR-C5).
    baseline = data.get("baseline") or {}
    if baseline:
        expected_digest = str(baseline.get("rules_sha256") or "")
        baseline_rules = [
            (
                str(r.get("schema_file")),
                str(r.get("class_name")),
                int(r.get("rule_index")),
                str(r.get("inv_id")),
            )
            for r in (baseline.get("rules") or [])
        ]
        baseline_triples = [(f, c, i) for f, c, i, _ in baseline_rules]
        actual = list_schema_rules(root)
        if baseline_triples != actual:
            errors.append(
                "baseline rules list differs from schemas: "
                f"matrix={len(baseline_triples)} schemas={len(actual)}"
            )
        digest = sha256_text(canon_rules(baseline_triples))
        if expected_digest and digest != expected_digest:
            errors.append(
                f"rules_sha256 mismatch: matrix={expected_digest} computed={digest}"
            )
        for f, c, i, inv_id in baseline_rules:
            inv = by_id.get(inv_id)
            if inv is None:
                errors.append(f"baseline {inv_id}: missing invariant row")
                continue
            lr = ((inv.get("implementation") or {}).get("linkml_rule")) or {}
            if (
                lr.get("schema_file") != f
                or lr.get("class_name") != c
                or int(lr.get("rule_index", -1)) != i
            ):
                errors.append(
                    f"{inv_id}: implementation.linkml_rule must be {f}/{c}/{i}, got {lr}"
                )

    actual = list_schema_rules(root)
    covered = {
        (
            str(lr.get("schema_file")),
            str(lr.get("class_name")),
            int(lr.get("rule_index")),
        )
        for inv in invs
        for lr in [((inv.get("implementation") or {}).get("linkml_rule"))]
        if lr
    }
    for triple in actual:
        if triple not in covered:
            errors.append(f"schema rule without matrix row: {triple}")

    # INV-prefix on every schema rule + matrix row (replaces baseline pin)
    for f, c, i, desc in list_schema_rules_detailed(root):
        m = INV_PREFIX_RE.match(desc.strip())
        if not m:
            errors.append(
                f"schema rule {f}/{c}/{i}: description must start with INV-NNN:, got {desc!r}"
            )
            continue
        inv_id = m.group(1)
        if inv_id not in by_id:
            errors.append(f"schema rule {f}/{c}/{i}: {inv_id} missing from matrix")

    for inv in invs:
        iid = str(inv.get("id"))
        levels = [str(x) for x in (inv.get("levels") or [])]
        ls = dict(inv.get("level_status") or {})
        status = str(inv.get("status") or "")

        if not ls:
            errors.append(f"{iid}: missing level_status")
        else:
            for level in ("L1", "L2", "L3"):
                if level not in ls:
                    errors.append(f"{iid}: level_status missing {level}")
                    continue
                st = str(ls[level])
                if level in levels and st == "not-applicable":
                    errors.append(
                        f"{iid}: level_status.{level}=not-applicable but {level} in levels"
                    )
                if level not in levels and st not in ("not-applicable",):
                    errors.append(
                        f"{iid}: level_status.{level}={st} but {level} not in levels "
                        "(use not-applicable)"
                    )

            computed = compute_overall_status(levels, {k: str(v) for k, v in ls.items()})
            if status and status != computed:
                errors.append(
                    f"{iid}: status={status!r} != computed from level_status={computed!r}"
                )

        # waived at overall or any level requires reason + adr_ref
        waived_levels = [
            level
            for level in ("L1", "L2", "L3")
            if str(ls.get(level)) == "waived"
        ]
        if status == "waived" or waived_levels:
            if not inv.get("waiver_reason"):
                errors.append(f"{iid}: waived without waiver_reason")
            if not inv.get("adr_ref"):
                errors.append(f"{iid}: waived without adr_ref")

        # File existence for implemented levels
        tests = inv.get("tests") or {}
        for level in levels:
            st = str(ls.get(level) or "")
            if st != "implemented":
                continue
            key = level.lower()
            valid = tests.get(f"{key}_valid") or []
            invalid = tests.get(f"{key}_invalid") or []
            if not valid or not invalid:
                errors.append(
                    f"{iid}: level_status.{level}=implemented requires "
                    f"{key}_valid and {key}_invalid"
                )
            for path in list(valid) + list(invalid):
                p = root / str(path)
                if not p.is_file():
                    errors.append(f"{iid}: missing test file {path}")

        # dams_validator: required callable when L2 implemented; forbidden otherwise
        impl = inv.get("implementation") or {}
        dv = impl.get("dams_validator")
        if str(ls.get("L2")) == "implemented":
            if not dv:
                errors.append(f"{iid}: L2 implemented requires implementation.dams_validator")
            else:
                try:
                    resolve_dams_validator(str(dv))
                except Exception as exc:  # noqa: BLE001 — surface path errors as matrix errors
                    errors.append(f"{iid}: dams_validator {dv!r}: {exc}")
        elif dv:
            errors.append(
                f"{iid}: dams_validator set but level_status.L2="
                f"{ls.get('L2')!r} (use not-applicable / waived without stub)"
            )

        if run_fixtures:
            if str(ls.get("L1")) == "implemented":
                _run_l1_fixtures(inv, root=root, errors=errors)
            if str(ls.get("L2")) == "implemented":
                _run_l2_fixtures(inv, root=root, errors=errors)
            if str(ls.get("L3")) == "implemented":
                _run_l3_fixtures(inv, root=root, errors=errors)

        if gate_strict and status in ("planned", "implemented-untested"):
            errors.append(
                f"{iid}: gate_strict forbids overall status={status!r} "
                "(publish-gate / PR-C5)"
            )

    return errors


def _run_l3_fixtures(
    inv: dict[str, Any], *, root: Path, errors: list[str]
) -> None:
    """Valid TTL conforms; invalid fails; report should mention INV id / sourceShape."""
    try:
        from pyshacl import validate
        from rdflib import Graph
    except ImportError:
        errors.append(f"{inv.get('id')}: pyshacl/rdflib required for L3 runner")
        return

    iid = str(inv.get("id"))
    shacl_rel = ((inv.get("implementation") or {}).get("shacl")) or ""
    if not shacl_rel:
        errors.append(f"{iid}: L3 implemented requires implementation.shacl")
        return
    shapes_path = root / str(shacl_rel)
    if not shapes_path.is_file():
        errors.append(f"{iid}: missing SHACL file {shacl_rel}")
        return

    tests = inv.get("tests") or {}
    valid_paths = [p for p in (tests.get("l3_valid") or []) if str(p).endswith(".ttl")]
    invalid_paths = [
        p for p in (tests.get("l3_invalid") or []) if str(p).endswith(".ttl")
    ]
    if not valid_paths or not invalid_paths:
        errors.append(f"{iid}: L3 implemented requires l3_valid/l3_invalid .ttl")
        return

    shapes = Graph().parse(shapes_path, format="turtle")
    for vp in valid_paths:
        path = root / str(vp)
        if not path.is_file():
            errors.append(f"{iid}: missing L3 valid fixture {vp}")
            continue
        data = Graph().parse(path, format="turtle")
        conforms, _, text = validate(
            data_graph=data, shacl_graph=shapes, inference="none", abort_on_first=False
        )
        if not conforms:
            errors.append(f"{iid}: L3 valid must conform: {vp}: {text[:200]}")

    for ip in invalid_paths:
        path = root / str(ip)
        if not path.is_file():
            errors.append(f"{iid}: missing L3 invalid fixture {ip}")
            continue
        data = Graph().parse(path, format="turtle")
        conforms, _, text = validate(
            data_graph=data, shacl_graph=shapes, inference="none", abort_on_first=False
        )
        if conforms:
            errors.append(f"{iid}: L3 invalid must fail: {ip}")
        elif iid not in text and f"Shape-{iid}" not in text:
            errors.append(
                f"{iid}: L3 invalid report must mention {iid} or Shape-{iid}: {ip}"
            )


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "---",
        "status: Proposed",
        'version: "0.1"',
        "normative: false",
        "supersedes: []",
        "superseded_by: []",
        "---",
        "",
        "# Constraint matrix (ADR-045)",
        "",
        "Автогенерируется `scripts/check_constraint_matrix.py`. "
        "Источник: "
        "`model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml`. "
        "Не редактировать вручную.",
        "",
        f"**matrix_id:** `{data.get('matrix_id')}`  ",
        f"**registry size:** {len(data.get('invariant_id_registry') or [])}  ",
        f"**invariants:** {len(data.get('invariants') or [])}",
        "",
        "| ID | Title | Levels | Status | L1 | L2 | L3 | Source status | Scope | Source |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for inv in data.get("invariants") or []:
        levels = ", ".join(inv.get("levels") or [])
        ls = inv.get("level_status") or {}
        lines.append(
            "| {id} | {title} | {levels} | {status} | {l1} | {l2} | {l3} | {ss} | {scope} | {source} |".format(
                id=inv.get("id"),
                title=str(inv.get("title") or "").replace("|", "\\|"),
                levels=levels,
                status=inv.get("status"),
                l1=ls.get("L1", ""),
                l2=ls.get("L2", ""),
                l3=ls.get("L3", ""),
                ss=inv.get("source_status"),
                scope=inv.get("scope"),
                source=str(inv.get("source") or "").replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Statements", ""])
    for inv in data.get("invariants") or []:
        lines.append(f"### {inv.get('id')}: {inv.get('title')}")
        lines.append("")
        lines.append(str(inv.get("statement") or ""))
        lines.append("")
        if inv.get("notes"):
            lines.append(f"*Notes:* {inv['notes']}")
            lines.append("")
        if inv.get("requirement_refs"):
            refs = ", ".join(f"`{r}`" for r in inv["requirement_refs"])
            lines.append(f"*requirement_refs:* {refs}")
            lines.append("")
        if inv.get("adr_ref"):
            lines.append(f"*adr_ref:* `{inv['adr_ref']}`")
            lines.append("")
    lines.append(
        "См. также: [ADR-045](../adr/ADR-045-executable-constraint-matrix.md), "
        "[inventory report](constraint-matrix-inventory-report.md), "
        "[adding-an-invariant](../guides/adding-an-invariant.md)."
    )
    lines.append("")
    return "\n".join(lines)


def run_check(
    *,
    write_doc: bool = True,
    root: Path | None = None,
    run_fixtures: bool = True,
    gate_strict: bool = False,
) -> tuple[int, list[str]]:
    """Load matrix, validate, optionally write markdown. Return (exit_code, errors)."""
    root = root or repo_root()
    data = load_yaml(matrix_path(root))
    errors = validate_matrix(
        data, root=root, run_fixtures=run_fixtures, gate_strict=gate_strict
    )
    if write_doc:
        out = doc_out_path(root)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(data), encoding="utf-8", newline="\n")
    return (1 if errors else 0, errors)
