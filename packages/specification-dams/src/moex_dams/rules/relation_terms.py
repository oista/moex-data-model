"""ADR-026 checks for RelationTerm dictionary and Relationship term refs."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody


def _diag(
    code: str,
    severity: DiagnosticSeverity,
    message: str,
    subject: str | None,
    *,
    remediation: str | None = None,
) -> Diagnostic:
    parts = [message]
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if remediation and str(remediation).strip():
        parts.append(f"Remediation: {remediation}")
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation).strip(),
            )
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def _term_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for term in data.get("relation_terms") or []:
        if not isinstance(term, dict):
            continue
        tid = str(term.get("element_id") or "")
        if tid:
            out[tid] = term
    return out


def relation_label(
    term: dict[str, Any],
    *,
    direction: str = "forward",
    language: str = "ru",
) -> str | None:
    """Return the label for a RelationTerm in the given direction/language."""
    symmetric = bool(term.get("symmetric"))
    if language == "en":
        forward = term.get("forward_label_en") or term.get("forward_label")
        inverse = term.get("inverse_label_en") or term.get("inverse_label")
    else:
        forward = term.get("forward_label")
        inverse = term.get("inverse_label")
    if direction == "inverse" and not symmetric:
        label = inverse or forward
    else:
        label = forward
    if isinstance(label, str) and label.strip():
        return label.strip()
    return None


def check_relation_terms(data: dict[str, Any]) -> list[Diagnostic]:
    """Validate RelationTerm entries and Relationship.relation_term_ref (ADR-026)."""
    out: list[Diagnostic] = []
    terms = _term_map(data)
    scope = str(data.get("implementation_scope") or "")

    for tid, term in terms.items():
        forward = term.get("forward_label")
        if not (isinstance(forward, str) and forward.strip()):
            out.append(
                _diag(
                    "DAMS-CM-RELTERM-001",
                    DiagnosticSeverity.ERROR,
                    f'RelationTerm "{tid}" requires forward_label.',
                    tid,
                )
            )
        symmetric = bool(term.get("symmetric"))
        inverse = term.get("inverse_label")
        if not symmetric and not (isinstance(inverse, str) and inverse.strip()):
            out.append(
                _diag(
                    "DAMS-CM-RELTERM-002",
                    DiagnosticSeverity.ERROR,
                    (
                        f'RelationTerm "{tid}" is not symmetric and requires '
                        "inverse_label."
                    ),
                    tid,
                    remediation="Set inverse_label or mark symmetric: true.",
                )
            )

    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        rid = str(rel.get("element_id") or rel.get("name") or "")
        term_ref = rel.get("relation_term_ref")
        direction = str(rel.get("term_direction") or "forward")
        lifecycle = str(rel.get("lifecycle_status") or "")

        if term_ref:
            tref = str(term_ref)
            if tref not in terms:
                out.append(
                    _diag(
                        "DAMS-CM-RELTERM-003",
                        DiagnosticSeverity.ERROR,
                        (
                            f'Relationship "{rid}" relation_term_ref {tref!r} '
                            "does not resolve in this package."
                        ),
                        rid,
                        remediation="Add the RelationTerm or fix the reference.",
                    )
                )
            elif direction not in ("forward", "inverse"):
                out.append(
                    _diag(
                        "DAMS-CM-RELTERM-004",
                        DiagnosticSeverity.ERROR,
                        (
                            f'Relationship "{rid}" has invalid '
                            f"term_direction={direction!r}."
                        ),
                        rid,
                    )
                )
        elif (
            scope == "enterprise"
            and lifecycle == "active"
            and terms  # only warn once a dictionary exists
        ):
            out.append(
                _diag(
                    "DAMS-CM-RELTERM-005",
                    DiagnosticSeverity.WARNING,
                    (
                        f'Active enterprise Relationship "{rid}" has no '
                        "relation_term_ref (transitional ADR-026)."
                    ),
                    rid,
                    remediation="Assign a RelationTerm with forward/inverse labels.",
                )
            )

    return out


def check_relation_terms_body(
    body: LinkMLImplementationBody,
) -> tuple[Diagnostic, ...]:
    return tuple(check_relation_terms(body.data))
