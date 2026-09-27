"""Application ports — no SQLAlchemy imports here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ValidationRunRecord:
    id: str
    implementation_id: str
    overall_result: str
    reported_at: str


@dataclass(frozen=True, slots=True)
class DiagnosticRecord:
    run_id: str
    code: str
    severity: str
    message: str


class ValidationRunStore(Protocol):
    def save_run(
        self,
        run: ValidationRunRecord,
        diagnostics: list[DiagnosticRecord],
    ) -> None: ...

    def get_run(self, run_id: str) -> ValidationRunRecord | None: ...


class WorkspaceStore(Protocol):
    def ensure_workspace(self, workspace_id: str, name: str) -> None: ...
