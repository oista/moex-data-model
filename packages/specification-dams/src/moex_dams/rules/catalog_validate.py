"""Semantic self-validation of DAMS RequirementCatalog instances (ADR-013)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CODE_PATTERN = re.compile(r"^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$")

ALLOWED_KINDS = frozenset(
    {
        "slot_required",
        "slot_min_cardinality",
        "ref_resolves",
        "key_subset",
        "at_least_one_slots",
        "conditional_branch",
        "definition_resolvable",
        "custom",
    }
)

ALLOWED_TARGET_CLASSES = frozenset(
    {
        "ModelPackage",
        "LogicalEntity",
        "LogicalAttribute",
        "Relationship",
        "PhysicalObject",
        "PhysicalField",
        "Mapping",
        "DomainContext",
        "ConceptualEntity",
    }
)

ALLOWED_OBJECT_KINDS = frozenset(
    {
        "database",
        "schema",
        "table",
        "view",
        "column",
        "api",
        "endpoint",
        "payload",
        "topic",
        "queue",
        "message",
        "file",
        "dataset",
        "pipeline",
    }
)

ALLOWED_SEVERITIES = frozenset({"error", "warning"})


@dataclass(frozen=True)
class CatalogIssue:
    code: str
    message: str
    subject: str | None = None


def validate_requirement_catalog(data: dict[str, Any]) -> list[CatalogIssue]:
    """Return semantic issues for a RequirementCatalog dict (empty = OK)."""
    issues: list[CatalogIssue] = []
    reqs = data.get("requirements") or []
    if not isinstance(reqs, list) or not reqs:
        issues.append(
            CatalogIssue("CATALOG-EMPTY", "RequirementCatalog.requirements is empty")
        )
        return issues

    seen_element_ids: dict[str, str] = {}
    seen_codes: dict[str, str] = {}
    seen_check_ids: dict[str, str] = {}

    for req in reqs:
        if not isinstance(req, dict):
            issues.append(CatalogIssue("CATALOG-REQ-TYPE", "requirement is not a mapping"))
            continue
        eid = str(req.get("element_id") or "")
        code = str(req.get("code") or "")
        label = code or eid or "<unknown>"

        if not eid:
            issues.append(CatalogIssue("CATALOG-ID-MISSING", "requirement missing element_id", label))
        elif eid in seen_element_ids:
            issues.append(
                CatalogIssue(
                    "CATALOG-ID-DUP",
                    f"duplicate element_id {eid!r} (also on {seen_element_ids[eid]})",
                    label,
                )
            )
        else:
            seen_element_ids[eid] = label

        if not code:
            issues.append(CatalogIssue("CATALOG-CODE-MISSING", "requirement missing code", eid or label))
        elif not CODE_PATTERN.match(code):
            issues.append(
                CatalogIssue(
                    "CATALOG-CODE-PATTERN",
                    f"code {code!r} does not match SECTION-NNN",
                    label,
                )
            )
        elif code in seen_codes:
            issues.append(
                CatalogIssue(
                    "CATALOG-CODE-DUP",
                    f"duplicate code {code!r} (also on {seen_codes[code]})",
                    label,
                )
            )
        else:
            seen_codes[code] = eid or label

        statement = req.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            issues.append(
                CatalogIssue(
                    "CATALOG-STATEMENT-MISSING",
                    "statement must be non-empty plain-language text",
                    label,
                )
            )

        applies = req.get("applies_to")
        if not isinstance(applies, dict) or not applies:
            issues.append(
                CatalogIssue(
                    "CATALOG-APPLIES-MISSING",
                    "applies_to is required",
                    label,
                )
            )
            applies_target = ""
        else:
            applies_target = str(applies.get("applies_target_class") or "").strip()
            if not applies_target:
                issues.append(
                    CatalogIssue(
                        "CATALOG-APPLIES-TARGET",
                        "applies_to.applies_target_class is required",
                        label,
                    )
                )
            elif applies_target not in ALLOWED_TARGET_CLASSES:
                issues.append(
                    CatalogIssue(
                        "CATALOG-TARGET-CLASS",
                        f"unknown applies_target_class {applies_target!r}",
                        label,
                    )
                )
            kinds = applies.get("applies_target_kinds") or []
            if isinstance(kinds, list):
                for k in kinds:
                    if str(k) not in ALLOWED_OBJECT_KINDS:
                        issues.append(
                            CatalogIssue(
                                "CATALOG-OBJECT-KIND",
                                f"unknown applies_target_kinds value {k!r}",
                                label,
                            )
                        )

        checks = req.get("formal_checks") or []
        if not isinstance(checks, list) or not checks:
            issues.append(
                CatalogIssue(
                    "CATALOG-CHECKS-MISSING",
                    "formal_checks must contain at least one check",
                    label,
                )
            )
            continue

        for check in checks:
            if not isinstance(check, dict):
                issues.append(
                    CatalogIssue("CATALOG-CHECK-TYPE", "formal_check is not a mapping", label)
                )
                continue
            cid = str(check.get("check_id") or "")
            if not cid:
                issues.append(
                    CatalogIssue("CATALOG-CHECK-ID-MISSING", "check_id required", label)
                )
            elif cid in seen_check_ids:
                issues.append(
                    CatalogIssue(
                        "CATALOG-CHECK-ID-DUP",
                        f"duplicate check_id {cid!r} (also on {seen_check_ids[cid]})",
                        label,
                    )
                )
            else:
                seen_check_ids[cid] = label

            kind = str(check.get("kind") or "")
            if kind not in ALLOWED_KINDS:
                issues.append(
                    CatalogIssue(
                        "CATALOG-CHECK-KIND",
                        f"unsupported formal_check kind {kind!r}",
                        cid or label,
                    )
                )

            sev = str(check.get("severity") or "")
            if sev not in ALLOWED_SEVERITIES:
                issues.append(
                    CatalogIssue(
                        "CATALOG-SEVERITY",
                        f"invalid severity {sev!r}",
                        cid or label,
                    )
                )

            tclass = str(check.get("target_class") or applies_target or "")
            if tclass and tclass not in ALLOWED_TARGET_CLASSES:
                issues.append(
                    CatalogIssue(
                        "CATALOG-TARGET-CLASS",
                        f"unknown target_class {tclass!r}",
                        cid or label,
                    )
                )

            if kind == "conditional_branch" and not str(check.get("expression") or "").strip():
                issues.append(
                    CatalogIssue(
                        "CATALOG-EXPRESSION-MISSING",
                        "conditional_branch requires expression (template name)",
                        cid or label,
                    )
                )

            if sev == "error":
                if not str(check.get("diagnostic_code") or "").strip():
                    issues.append(
                        CatalogIssue(
                            "CATALOG-DIAG-MISSING",
                            "error checks require diagnostic_code",
                            cid or label,
                        )
                    )
                if not str(check.get("remediation") or "").strip():
                    issues.append(
                        CatalogIssue(
                            "CATALOG-REMEDIATION-MISSING",
                            "error checks require remediation",
                            cid or label,
                        )
                    )

    return issues


def validate_requirement_catalog_file(path: Path) -> list[CatalogIssue]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return [CatalogIssue("CATALOG-ROOT", f"{path} is not a YAML mapping")]
    return validate_requirement_catalog(raw)


def main(argv: list[str] | None = None) -> int:
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: catalog_validate <catalog.yaml> [...]", file=sys.stderr)
        return 2
    failed = 0
    for arg in args:
        path = Path(arg)
        issues = validate_requirement_catalog_file(path)
        if issues:
            failed += 1
            print(f"FAIL {path}", file=sys.stderr)
            for iss in issues:
                subj = f" [{iss.subject}]" if iss.subject else ""
                print(f"  {iss.code}{subj}: {iss.message}", file=sys.stderr)
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
