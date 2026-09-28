"""Application ports — no SQLAlchemy imports here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: str
    display_name: str


@dataclass(frozen=True, slots=True)
class WorkspaceRecord:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class WorkspaceMemberRecord:
    workspace_id: str
    user_id: str
    role: str


@dataclass(frozen=True, slots=True)
class ValidationRunRecord:
    id: str
    implementation_id: str
    overall_result: str
    reported_at: str
    workspace_id: str | None = None
    job_id: str | None = None


@dataclass(frozen=True, slots=True)
class DiagnosticRecord:
    run_id: str
    code: str
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class JobRecord:
    id: str
    workspace_id: str
    kind: str
    status: str
    implementation_id: str
    idempotency_key: str | None
    payload_fingerprint: str
    result_summary: str
    finished_at: str | None = None


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    id: str
    job_id: str
    kind: str
    path_or_uri: str
    content_digest: str


@dataclass(frozen=True, slots=True)
class ElementHit:
    element_id: str
    element_kind: str
    name: str
    layer: str
    implementation_id: str


@dataclass(frozen=True, slots=True)
class IndexElement:
    element_id: str
    element_kind: str
    name: str
    layer: str = ""


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    workspace_id: str
    doc_key: str
    content: str
    base_digest: str
    updated_by: str


class IdentityStore(Protocol):
    def ensure_user(self, actor: str, display_name: str | None = None) -> UserRecord: ...

    def bind_role(self, user_id: str, role: str) -> None: ...

    def list_roles(self, user_id: str) -> list[str]: ...


class WorkspaceStore(Protocol):
    def ensure_workspace(self, workspace_id: str, name: str) -> None: ...

    def create(self, workspace_id: str, name: str) -> WorkspaceRecord: ...

    def get(self, workspace_id: str) -> WorkspaceRecord | None: ...

    def list_for_user(self, user_id: str) -> list[WorkspaceRecord]: ...

    def add_member(
        self, workspace_id: str, user_id: str, role: str = "owner"
    ) -> None: ...

    def list_members(self, workspace_id: str) -> list[WorkspaceMemberRecord]: ...


class ValidationRunStore(Protocol):
    def save_run(
        self,
        run: ValidationRunRecord,
        diagnostics: list[DiagnosticRecord],
        *,
        actor: str = "dev",
    ) -> None: ...

    def get_run(self, run_id: str) -> ValidationRunRecord | None: ...


class JobStore(Protocol):
    def create_job(self, job: JobRecord) -> JobRecord: ...

    def get_job(self, job_id: str) -> JobRecord | None: ...

    def get_by_idempotency(self, key: str) -> JobRecord | None: ...

    def update_status(
        self,
        job_id: str,
        status: str,
        *,
        result_summary: str = "",
        finished_at: str | None = None,
    ) -> JobRecord: ...

    def attach_artifact(self, artifact: ArtifactRecord) -> None: ...

    def list_artifacts(self, job_id: str) -> list[ArtifactRecord]: ...


class ModelIndexProvider(Protocol):
    def rebuild(
        self,
        *,
        index_id: str,
        implementation_id: str,
        revision: str,
        content_digest: str,
        indexed_at: str,
        elements: list[IndexElement],
    ) -> str: ...

    def search(self, q: str, *, limit: int = 50) -> list[ElementHit]: ...


class AuditStore(Protocol):
    def record(self, action: str, actor: str, detail: str = "") -> None: ...


class DocumentStore(Protocol):
    def get(self, workspace_id: str, doc_key: str) -> DocumentRecord | None: ...

    def upsert(
        self,
        *,
        workspace_id: str,
        doc_key: str,
        content: str,
        base_digest: str,
        updated_by: str,
    ) -> DocumentRecord: ...


@dataclass(frozen=True, slots=True)
class PublicationRecord:
    id: str
    workspace_id: str
    implementation_id: str
    doc_key: str
    branch_name: str
    base_revision: str
    commit_sha: str
    review_url: str
    review_id: str
    status: str
    actor: str
    idempotency_key: str | None
    payload_fingerprint: str


class PublicationStore(Protocol):
    def create(self, row: PublicationRecord) -> PublicationRecord: ...

    def get(self, publication_id: str) -> PublicationRecord | None: ...

    def get_by_idempotency(self, key: str) -> PublicationRecord | None: ...
