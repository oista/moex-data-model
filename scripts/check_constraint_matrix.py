"""Validate constraint-matrix.yaml against its schema and structural rules (ADR-045 / PR-C1).

Checks
  * LinkML instance validation via ``make_linkml_validator`` (closed JSON Schema)
  * baseline rules list matches schemas exactly (file|class|index), sha256 and count
  * every schema rule has a matrix row with matching ``implementation.linkml_rule``
  * every ``implemented`` row has valid+invalid tests for each declared level
  * ``waived`` requires ``waiver_reason``
  * regenerates ``docs/architecture/constraint-matrix.md`` (``--write-doc`` / default)

Usage (repo root)::

    python scripts/check_constraint_matrix.py
    python scripts/check_constraint_matrix.py --no-write-doc
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
MATRIX = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "constraints"
    / "constraint-matrix.yaml"
)
SCHEMA = MATRIX.with_name("constraint-matrix.schema.yaml")
SCHEMA_DIR = (
    REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "schemas"
)
DOC_OUT = REPO / "docs" / "architecture" / "constraint-matrix.md"


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _schema_rules() -> list[tuple[str, str, int]]:
    # Prefer inventory helper (ruamel) when available; fall back to PyYAML.
    try:
        from inventory_invariants import list_rules  # type: ignore

        return [(f, c, i) for f, c, i, _ in list_rules()]
    except Exception:
        out: list[tuple[str, str, int]] = []
        for path in sorted(SCHEMA_DIR.glob("*.yaml")):
            data = _load(path) or {}
            for cname, body in (data.get("classes") or {}).items():
                for idx, _rule in enumerate((body or {}).get("rules") or []):
                    out.append((path.name, cname, idx))
        return out


def _canon(rules: list[tuple[str, str, int]]) -> str:
    return "\n".join(f"{f}|{c}|{i}" for f, c, i in rules) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_matrix(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # 1) Schema validation
    sys.path.insert(0, str(REPO / "packages" / "standard-linkml" / "src"))
    from moex_standard_linkml.validation import error_results, make_linkml_validator

    report = make_linkml_validator(SCHEMA).validate(
        data, target_class="ConstraintMatrix"
    )
    for item in error_results(report):
        errors.append(f"schema: {getattr(item, 'message', item)}")

    baseline = data.get("baseline") or {}
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
    actual = _schema_rules()
    if baseline_triples != actual:
        errors.append(
            "baseline rules list differs from schemas: "
            f"matrix={len(baseline_triples)} schemas={len(actual)}"
        )
        for a, b in zip(baseline_triples, actual):
            if a != b:
                errors.append(f"  mismatch: matrix={a} schema={b}")
                break
        if len(actual) > len(baseline_triples):
            errors.append(
                f"  extra schema rules (first): {actual[len(baseline_triples):len(baseline_triples)+3]}"
            )
        if len(baseline_triples) > len(actual):
            errors.append(
                f"  extra matrix baseline (first): {baseline_triples[len(actual):len(actual)+3]}"
            )

    canon = _canon(baseline_triples)
    digest = _sha256_text(canon)
    if expected_digest and digest != expected_digest:
        errors.append(
            f"rules_sha256 mismatch: matrix={expected_digest} computed={digest}"
        )

    invs = list(data.get("invariants") or [])
    by_id = {str(inv.get("id")): inv for inv in invs}
    if len(by_id) != len(invs):
        errors.append("duplicate invariant id")

    # Every baseline inv_id exists and points back
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

    # Every schema rule covered by some linkml_rule
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

    for inv in invs:
        iid = str(inv.get("id"))
        status = str(inv.get("status") or "")
        if status == "waived" and not inv.get("waiver_reason"):
            errors.append(f"{iid}: waived without waiver_reason")
        if status == "implemented":
            levels = list(inv.get("levels") or [])
            tests = inv.get("tests") or {}
            for level in levels:
                key = str(level).lower()  # L1 -> l1
                valid = tests.get(f"{key}_valid") or []
                invalid = tests.get(f"{key}_invalid") or []
                if not valid or not invalid:
                    errors.append(
                        f"{iid}: implemented requires {key}_valid and {key}_invalid"
                    )
                for path in list(valid) + list(invalid):
                    p = REPO / str(path)
                    if not p.is_file():
                        errors.append(f"{iid}: missing test file {path}")

    return errors


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
        f"**baseline_commit:** `{((data.get('baseline') or {}).get('baseline_commit'))}`  ",
        f"**rules_sha256:** `{((data.get('baseline') or {}).get('rules_sha256'))}`  ",
        f"**rules in baseline:** {len(((data.get('baseline') or {}).get('rules') or []))}",
        "",
        "| ID | Title | Levels | Status | Source status | Scope | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    for inv in data.get("invariants") or []:
        levels = ", ".join(inv.get("levels") or [])
        lines.append(
            "| {id} | {title} | {levels} | {status} | {ss} | {scope} | {source} |".format(
                id=inv.get("id"),
                title=str(inv.get("title") or "").replace("|", "\\|"),
                levels=levels,
                status=inv.get("status"),
                ss=inv.get("source_status"),
                scope=inv.get("scope"),
                source=str(inv.get("source") or "").replace("|", "\\|"),
            )
        )
    lines.extend(
        [
            "",
            "## Statements",
            "",
        ]
    )
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
    lines.append(
        "См. также: [ADR-045](../adr/ADR-045-executable-constraint-matrix.md), "
        "[inventory report](constraint-matrix-inventory-report.md), "
        "[adding-an-invariant](../guides/adding-an-invariant.md)."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--no-write-doc",
        action="store_true",
        help="Do not write docs/architecture/constraint-matrix.md",
    )
    ap.add_argument(
        "--write-doc",
        action="store_true",
        help="Write generated markdown (default)",
    )
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Allow importing scripts/inventory_invariants.py
    sys.path.insert(0, str(REPO / "scripts"))

    data = _load(MATRIX)
    errors = validate_matrix(data)
    write_doc = not args.no_write_doc
    if write_doc:
        DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
        DOC_OUT.write_text(render_markdown(data), encoding="utf-8", newline="\n")
        print(f"wrote {DOC_OUT.relative_to(REPO).as_posix()}")

    if errors:
        print(f"check-constraints FAIL ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        f"check-constraints OK invariants={len(data.get('invariants') or [])} "
        f"baseline_rules={len(((data.get('baseline') or {}).get('rules') or []))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
