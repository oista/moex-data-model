"""SQLAlchemy implementations of application ports."""

from __future__ import annotations

from sqlalchemy.orm import Session

from moex_model_api.db import models as orm
from moex_model_api.ports import DiagnosticRecord, ValidationRunRecord


class SqlValidationRunStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_run(
        self,
        run: ValidationRunRecord,
        diagnostics: list[DiagnosticRecord],
    ) -> None:
        row = orm.ValidationRun(
            id=run.id,
            implementation_id=run.implementation_id,
            overall_result=run.overall_result,
            reported_at=run.reported_at,
        )
        self._session.add(row)
        for d in diagnostics:
            self._session.add(
                orm.ValidationDiagnostic(
                    run_id=run.id,
                    code=d.code,
                    severity=d.severity,
                    message=d.message,
                )
            )
        self._session.add(
            orm.AuditEvent(
                action="validation_run.save",
                actor="dev",
                detail=run.id,
            )
        )
        self._session.flush()

    def get_run(self, run_id: str) -> ValidationRunRecord | None:
        row = self._session.get(orm.ValidationRun, run_id)
        if row is None:
            return None
        return ValidationRunRecord(
            id=row.id,
            implementation_id=row.implementation_id,
            overall_result=row.overall_result,
            reported_at=row.reported_at,
        )


class SqlWorkspaceStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_workspace(self, workspace_id: str, name: str) -> None:
        existing = self._session.get(orm.Workspace, workspace_id)
        if existing is None:
            self._session.add(orm.Workspace(id=workspace_id, name=name))
            self._session.flush()
