"""matrix-check — waiver expiry + requirement/check/result traceability."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

import yaml

from moex_dams.rules.constraint_matrix import (
    DIAGNOSTIC_CODE_ALIASES,
    canonical_diagnostic_code,
    matrix_path,
    validate_matrix,
)


def _parse_date(raw: Any) -> date | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    if isinstance(raw, datetime):
        return raw.date()
    text = str(raw).strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _is_waived(inv: dict[str, Any]) -> bool:
    if str(inv.get("status") or "") == "waived":
        return True
    ls = inv.get("level_status") or {}
    if isinstance(ls, dict):
        return any(str(ls.get(level)) == "waived" for level in ("L1", "L2", "L3"))
    return False


def check_waiver_expiry(
    data: dict[str, Any],
    *,
    today: date | None = None,
    warn_days: int = 14,
    require_expires: bool = True,
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for waived invariants' waiver_expires."""
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    for inv in data.get("invariants") or []:
        if not isinstance(inv, dict):
            continue
        iid = str(inv.get("id") or "?")
        if not _is_waived(inv):
            continue
        expires = _parse_date(inv.get("waiver_expires"))
        if expires is None:
            if require_expires:
                errors.append(f"{iid}: waived without waiver_expires (YYYY-MM-DD)")
            continue
        if expires < today:
            errors.append(f"{iid}: waiver_expires={expires.isoformat()} is past")
        elif expires <= today + timedelta(days=warn_days):
            warnings.append(
                f"{iid}: waiver_expires={expires.isoformat()} within {warn_days} days"
            )
    return errors, warnings


def _codes_for_inv(iid: str) -> set[str]:
    codes = {canonical_diagnostic_code(iid), iid}
    codes |= set(DIAGNOSTIC_CODE_ALIASES.get(iid, frozenset()))
    return codes


def _has_check(inv: dict[str, Any]) -> bool:
    impl = inv.get("implementation") or {}
    if not isinstance(impl, dict):
        return False
    return bool(impl.get("linkml_rule") or impl.get("dams_validator") or impl.get("shacl"))


def _hard_codes_from_ci_validate(payload: dict[str, Any] | None) -> set[str]:
    if not payload:
        return set()
    codes: set[str] = set()
    for impl in payload.get("implementations") or []:
        for diag in impl.get("errors") or []:
            code = str(diag.get("code") or "")
            if code:
                codes.add(code)
    return codes


def build_traceability(
    data: dict[str, Any],
    *,
    hard_codes: set[str] | None = None,
) -> dict[str, Any]:
    """Build requirement → check → result from matrix + optional CI hard codes."""
    hard_codes = hard_codes or set()
    rows: list[dict[str, Any]] = []
    problems: list[str] = []
    counts = {"pass": 0, "fail": 0, "waived": 0, "missing": 0}
    for inv in data.get("invariants") or []:
        if not isinstance(inv, dict):
            continue
        iid = str(inv.get("id") or "")
        status = str(inv.get("status") or "")
        impl = inv.get("implementation") or {}
        has_check = _has_check(inv)
        waived = _is_waived(inv)
        req_refs = [str(r) for r in (inv.get("requirement_refs") or [])]
        inv_codes = _codes_for_inv(iid)
        hit = bool(hard_codes & inv_codes)

        if waived:
            result = "waived"
        elif hit:
            result = "fail"
        elif not has_check or status in ("planned", "implemented-untested"):
            result = "missing"
            if not waived:
                problems.append(
                    f"{iid}: no check and not waived"
                    if not has_check
                    else f"{iid}: status={status} without implemented check"
                )
        else:
            result = "pass"

        counts[result] = counts.get(result, 0) + 1
        rows.append(
            {
                "id": iid,
                "requirement_refs": req_refs,
                "status": status,
                "has_check": has_check,
                "waived": waived,
                "result": result,
                "check": {
                    "linkml_rule": impl.get("linkml_rule") if isinstance(impl, dict) else None,
                    "dams_validator": impl.get("dams_validator")
                    if isinstance(impl, dict)
                    else None,
                    "shacl": impl.get("shacl") if isinstance(impl, dict) else None,
                },
            }
        )
    return {
        "rows": rows,
        "problems": problems,
        "counts": counts,
        "ok": not problems,
        "observed_hard_codes": sorted(hard_codes),
    }


def write_traceability_junit(path: Path, trace: dict[str, Any]) -> None:
    suite = Element(
        "testsuite",
        name="traceability",
        tests=str(len(trace.get("rows") or [])),
        failures=str(len(trace.get("problems") or [])),
    )
    for row in trace.get("rows") or []:
        case = SubElement(
            suite,
            "testcase",
            name=str(row.get("id") or "?"),
            classname="traceability",
        )
        result = str(row.get("result") or "")
        if result == "missing":
            failure = SubElement(case, "failure", message="no check and not waived")
            failure.text = result
        elif result == "fail":
            failure = SubElement(case, "failure", message="hard diagnostic matched")
            failure.text = result
        elif result == "waived":
            skipped = SubElement(case, "skipped")
            skipped.set("message", "waived")
    path.parent.mkdir(parents=True, exist_ok=True)
    root = Element("testsuites")
    root.append(suite)
    path.write_bytes(tostring(root, encoding="utf-8", xml_declaration=True))


def run_matrix_check(
    repo_root: Path,
    *,
    today: date | None = None,
    require_expires: bool = True,
    with_traceability: bool = True,
    ci_validate_json: Path | None = None,
    junit_path: Path | None = None,
    as_json: bool = False,
    warn_days: int = 14,
) -> tuple[int, str]:
    root = repo_root.resolve()
    path = matrix_path(root)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return 1, f"matrix-check: invalid matrix at {path}\n"

    structural = validate_matrix(data, root=root, run_fixtures=False, gate_strict=False)
    expiry_errors, expiry_warnings = check_waiver_expiry(
        data, today=today, warn_days=warn_days, require_expires=require_expires
    )

    hard_codes: set[str] = set()
    if ci_validate_json is not None:
        payload_path = (
            ci_validate_json
            if ci_validate_json.is_absolute()
            else root / ci_validate_json
        )
        if payload_path.is_file():
            hard_codes = _hard_codes_from_ci_validate(
                json.loads(payload_path.read_text(encoding="utf-8"))
            )

    trace: dict[str, Any] | None = None
    trace_problems: list[str] = []
    if with_traceability:
        trace = build_traceability(data, hard_codes=hard_codes)
        # Only missing checks block; fail is already covered by ci-validate.
        trace_problems = [
            p for p in (trace.get("problems") or []) if "no check" in p or "without implemented" in p
        ]
        if junit_path is not None:
            out = junit_path if junit_path.is_absolute() else root / junit_path
            write_traceability_junit(out, trace)

    problems = list(structural) + expiry_errors + trace_problems
    payload = {
        "structural_errors": structural,
        "expiry_errors": expiry_errors,
        "expiry_warnings": expiry_warnings,
        "traceability": trace,
        "ok": not problems,
    }
    if as_json:
        return (1 if problems else 0), json.dumps(payload, indent=2) + "\n"

    lines = [
        f"matrix-check structural={len(structural)} "
        f"expiry_errors={len(expiry_errors)} "
        f"expiry_warnings={len(expiry_warnings)} "
        f"trace_problems={len(trace_problems)}"
    ]
    if trace and trace.get("counts"):
        counts = trace["counts"]
        lines.append(
            f"  trace pass={counts.get('pass', 0)} fail={counts.get('fail', 0)} "
            f"waived={counts.get('waived', 0)} missing={counts.get('missing', 0)}"
        )
    for item in problems:
        lines.append(f"  FAIL {item}")
    for item in expiry_warnings:
        lines.append(f"  WARN {item}")
    if not problems:
        lines.append("matrix-check OK")
    return (1 if problems else 0), "\n".join(lines) + "\n"
