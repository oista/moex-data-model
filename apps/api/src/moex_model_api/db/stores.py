"""SQLAlchemy implementations of application ports."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from moex_model_api.db import models as orm
from moex_model_api.ports import (
    ArtifactRecord,
    DiagnosticRecord,
    DocumentRecord,
    ElementHit,
    IndexElement,
    JobRecord,
    UserRecord,
    ValidationRunRecord,
    WorkspaceMemberRecord,
    WorkspaceRecord,
)


class SqlAuditStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(self, action: str, actor: str, detail: str = "") -> None:
        self._session.add(
            orm.AuditEvent(action=action, actor=actor, detail=detail)
        )
        self._session.flush()


class SqlIdentityStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_user(self, actor: str, display_name: str | None = None) -> UserRecord:
        row = self._session.get(orm.UserIdentity, actor)
        if row is None:
            row = orm.UserIdentity(
                id=actor, display_name=display_name or actor
            )
            self._session.add(row)
            self._session.flush()
            self.bind_role(actor, "editor")
        return UserRecord(id=row.id, display_name=row.display_name)

    def bind_role(self, user_id: str, role: str) -> None:
        existing = self._session.scalars(
            select(orm.RoleBinding).where(
                orm.RoleBinding.user_id == user_id,
                orm.RoleBinding.role == role,
            )
        ).first()
        if existing is None:
            self._session.add(orm.RoleBinding(user_id=user_id, role=role))
            self._session.flush()

    def list_roles(self, user_id: str) -> list[str]:
        rows = self._session.scalars(
            select(orm.RoleBinding).where(orm.RoleBinding.user_id == user_id)
        ).all()
        return [r.role for r in rows]


class SqlWorkspaceStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_workspace(self, workspace_id: str, name: str) -> None:
        existing = self._session.get(orm.Workspace, workspace_id)
        if existing is None:
            self._session.add(orm.Workspace(id=workspace_id, name=name))
            self._session.flush()

    def create(self, workspace_id: str, name: str) -> WorkspaceRecord:
        existing = self._session.get(orm.Workspace, workspace_id)
        if existing is not None:
            return WorkspaceRecord(id=existing.id, name=existing.name)
        row = orm.Workspace(id=workspace_id, name=name)
        self._session.add(row)
        self._session.flush()
        return WorkspaceRecord(id=row.id, name=row.name)

    def get(self, workspace_id: str) -> WorkspaceRecord | None:
        row = self._session.get(orm.Workspace, workspace_id)
        if row is None:
            return None
        return WorkspaceRecord(id=row.id, name=row.name)

    def list_for_user(self, user_id: str) -> list[WorkspaceRecord]:
        rows = self._session.scalars(
            select(orm.Workspace)
            .join(
                orm.WorkspaceMember,
                orm.WorkspaceMember.workspace_id == orm.Workspace.id,
            )
            .where(orm.WorkspaceMember.user_id == user_id)
        ).all()
        return [WorkspaceRecord(id=r.id, name=r.name) for r in rows]

    def add_member(
        self, workspace_id: str, user_id: str, role: str = "owner"
    ) -> None:
        existing = self._session.get(
            orm.WorkspaceMember, {"workspace_id": workspace_id, "user_id": user_id}
        )
        if existing is None:
            self._session.add(
                orm.WorkspaceMember(
                    workspace_id=workspace_id, user_id=user_id, role=role
                )
            )
            self._session.flush()

    def list_members(self, workspace_id: str) -> list[WorkspaceMemberRecord]:
        rows = self._session.scalars(
            select(orm.WorkspaceMember).where(
                orm.WorkspaceMember.workspace_id == workspace_id
            )
        ).all()
        return [
            WorkspaceMemberRecord(
                workspace_id=r.workspace_id, user_id=r.user_id, role=r.role
            )
            for r in rows
        ]


class SqlValidationRunStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_run(
        self,
        run: ValidationRunRecord,
        diagnostics: list[DiagnosticRecord],
        *,
        actor: str = "dev",
    ) -> None:
        row = orm.ValidationRun(
            id=run.id,
            implementation_id=run.implementation_id,
            overall_result=run.overall_result,
            reported_at=run.reported_at,
            workspace_id=run.workspace_id,
            job_id=run.job_id,
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
                actor=actor,
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
            workspace_id=row.workspace_id,
            job_id=row.job_id,
        )


class SqlJobStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_job(self, job: JobRecord) -> JobRecord:
        row = orm.GenerationJob(
            id=job.id,
            workspace_id=job.workspace_id,
            kind=job.kind,
            status=job.status,
            implementation_id=job.implementation_id,
            idempotency_key=job.idempotency_key,
            payload_fingerprint=job.payload_fingerprint,
            result_summary=job.result_summary,
            finished_at=job.finished_at,
        )
        self._session.add(row)
        self._session.flush()
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        row = self._session.get(orm.GenerationJob, job_id)
        return None if row is None else self._to_record(row)

    def get_by_idempotency(self, key: str) -> JobRecord | None:
        row = self._session.scalars(
            select(orm.GenerationJob).where(
                orm.GenerationJob.idempotency_key == key
            )
        ).first()
        return None if row is None else self._to_record(row)

    def update_status(
        self,
        job_id: str,
        status: str,
        *,
        result_summary: str = "",
        finished_at: str | None = None,
    ) -> JobRecord:
        row = self._session.get(orm.GenerationJob, job_id)
        if row is None:
            raise KeyError(job_id)
        row.status = status
        if result_summary:
            row.result_summary = result_summary
        if finished_at is not None:
            row.finished_at = finished_at
        self._session.flush()
        return self._to_record(row)

    def attach_artifact(self, artifact: ArtifactRecord) -> None:
        self._session.add(
            orm.GeneratedArtifact(
                id=artifact.id,
                job_id=artifact.job_id,
                kind=artifact.kind,
                path_or_uri=artifact.path_or_uri,
                content_digest=artifact.content_digest,
            )
        )
        self._session.flush()

    def list_artifacts(self, job_id: str) -> list[ArtifactRecord]:
        rows = self._session.scalars(
            select(orm.GeneratedArtifact).where(
                orm.GeneratedArtifact.job_id == job_id
            )
        ).all()
        return [
            ArtifactRecord(
                id=r.id,
                job_id=r.job_id,
                kind=r.kind,
                path_or_uri=r.path_or_uri,
                content_digest=r.content_digest,
            )
            for r in rows
        ]

    @staticmethod
    def _to_record(row: orm.GenerationJob) -> JobRecord:
        return JobRecord(
            id=row.id,
            workspace_id=row.workspace_id,
            kind=row.kind,
            status=row.status,
            implementation_id=row.implementation_id,
            idempotency_key=row.idempotency_key,
            payload_fingerprint=row.payload_fingerprint,
            result_summary=row.result_summary,
            finished_at=row.finished_at,
        )


class SqlModelIndexProvider:
    def __init__(self, session: Session) -> None:
        self._session = session

    def rebuild(
        self,
        *,
        index_id: str,
        implementation_id: str,
        revision: str,
        content_digest: str,
        indexed_at: str,
        elements: list[IndexElement],
    ) -> str:
        # Drop prior indexes for same implementation_id
        prior = self._session.scalars(
            select(orm.ModelIndex).where(
                orm.ModelIndex.implementation_id == implementation_id
            )
        ).all()
        for p in prior:
            self._session.delete(p)
        self._session.flush()

        idx = orm.ModelIndex(
            id=index_id,
            implementation_id=implementation_id,
            revision=revision,
            content_digest=content_digest,
            indexed_at=indexed_at,
        )
        self._session.add(idx)
        for el in elements:
            self._session.add(
                orm.ModelElementIndex(
                    index_id=index_id,
                    element_id=el.element_id,
                    element_kind=el.element_kind,
                    name=el.name,
                    layer=el.layer,
                )
            )
        rev_id = f"rev:{implementation_id}:{revision}"
        existing_rev = self._session.get(orm.ModelRevisionIndex, rev_id)
        if existing_rev is None:
            self._session.add(
                orm.ModelRevisionIndex(
                    id=rev_id,
                    implementation_id=implementation_id,
                    revision=revision,
                    content_digest=content_digest,
                )
            )
        else:
            existing_rev.content_digest = content_digest
            existing_rev.revision = revision
        self._session.flush()
        return index_id

    def search(self, q: str, *, limit: int = 50) -> list[ElementHit]:
        needle = f"%{q}%"
        rows = self._session.execute(
            select(orm.ModelElementIndex, orm.ModelIndex)
            .join(
                orm.ModelIndex,
                orm.ModelElementIndex.index_id == orm.ModelIndex.id,
            )
            .where(
                or_(
                    orm.ModelElementIndex.element_id.ilike(needle),
                    orm.ModelElementIndex.name.ilike(needle),
                )
            )
            .limit(limit)
        ).all()
        return [
            ElementHit(
                element_id=el.element_id,
                element_kind=el.element_kind,
                name=el.name,
                layer=el.layer,
                implementation_id=idx.implementation_id,
            )
            for el, idx in rows
        ]


class SqlDocumentStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, workspace_id: str, doc_key: str) -> DocumentRecord | None:
        row = self._session.get(
            orm.WorkspaceDocument,
            {"workspace_id": workspace_id, "doc_key": doc_key},
        )
        if row is None:
            return None
        return DocumentRecord(
            workspace_id=row.workspace_id,
            doc_key=row.doc_key,
            content=row.content,
            base_digest=row.base_digest,
            updated_by=row.updated_by,
        )

    def upsert(
        self,
        *,
        workspace_id: str,
        doc_key: str,
        content: str,
        base_digest: str,
        updated_by: str,
    ) -> DocumentRecord:
        row = self._session.get(
            orm.WorkspaceDocument,
            {"workspace_id": workspace_id, "doc_key": doc_key},
        )
        if row is None:
            row = orm.WorkspaceDocument(
                workspace_id=workspace_id,
                doc_key=doc_key,
                content=content,
                base_digest=base_digest,
                updated_by=updated_by,
            )
            self._session.add(row)
        else:
            row.content = content
            row.base_digest = base_digest
            row.updated_by = updated_by
        self._session.flush()
        return DocumentRecord(
            workspace_id=row.workspace_id,
            doc_key=row.doc_key,
            content=row.content,
            base_digest=row.base_digest,
            updated_by=row.updated_by,
        )
