"""Diagnostic and source-location contracts for solution-xlsx import."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class SourceRef:
    """1-based Excel row; column is the workbook header name when known."""

    sheet: str
    row: int
    column: str | None = None

    def label(self) -> str:
        if self.column:
            return f"{self.sheet}!{self.column}:{self.row}"
        return f"{self.sheet}:{self.row}"


@dataclass
class Diagnostic:
    code: str
    severity: Severity
    message_ru: str
    remediation: str
    source_ref: SourceRef | None = None
    element_ref: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        if self.source_ref is not None:
            data["source_ref"] = asdict(self.source_ref)
            data["location"] = self.source_ref.label()
        return data

    def __str__(self) -> str:
        loc = f" @ {self.source_ref.label()}" if self.source_ref else ""
        return (
            f"[{self.severity.value.upper()}] {self.code}{loc}: "
            f"{self.message_ru} — {self.remediation}"
        )


def apply_severity_overrides(
    diagnostics: list[Diagnostic],
    overrides: dict[str, str],
) -> list[Diagnostic]:
    """Apply profile severity overrides by diagnostic code."""
    if not overrides:
        return diagnostics
    out: list[Diagnostic] = []
    for d in diagnostics:
        raw = overrides.get(d.code)
        if raw is None:
            out.append(d)
            continue
        try:
            sev = Severity(str(raw).strip().lower())
        except ValueError:
            out.append(d)
            continue
        out.append(
            Diagnostic(
                code=d.code,
                severity=sev,
                message_ru=d.message_ru,
                remediation=d.remediation,
                source_ref=d.source_ref,
                element_ref=d.element_ref,
                details=dict(d.details),
            )
        )
    return out


def strict_promote_warnings(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    """Promote warning → error for --strict mode."""
    out: list[Diagnostic] = []
    for d in diagnostics:
        if d.severity is Severity.WARNING:
            out.append(
                Diagnostic(
                    code=d.code,
                    severity=Severity.ERROR,
                    message_ru=d.message_ru,
                    remediation=d.remediation,
                    source_ref=d.source_ref,
                    element_ref=d.element_ref,
                    details=dict(d.details),
                )
            )
        else:
            out.append(d)
    return out


def has_errors(diagnostics: list[Diagnostic]) -> bool:
    return any(d.severity is Severity.ERROR for d in diagnostics)
