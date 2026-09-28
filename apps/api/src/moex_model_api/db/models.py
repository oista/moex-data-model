"""SQLAlchemy ORM models for operational tables (adapter layer only)."""

from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserIdentity(Base):
    __tablename__ = "user_identity"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RoleBinding(Base):
    __tablename__ = "role_binding"
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_role_binding"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("user_identity.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(64), nullable=False)


class Workspace(Base):
    __tablename__ = "workspace"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class WorkspaceMember(Base):
    __tablename__ = "workspace_member"

    workspace_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("workspace.id"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("user_identity.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="owner")


class WorkspaceDocument(Base):
    __tablename__ = "workspace_document"

    workspace_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("workspace.id"), primary_key=True
    )
    doc_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    base_digest: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    updated_by: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ModelRevisionIndex(Base):
    __tablename__ = "model_revision_index"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    implementation_id: Mapped[str] = mapped_column(String(256), nullable=False)
    revision: Mapped[str] = mapped_column(String(128), nullable=False)
    content_digest: Mapped[str] = mapped_column(String(128), nullable=False)


class ValidationRun(Base):
    __tablename__ = "validation_run"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    implementation_id: Mapped[str] = mapped_column(String(256), nullable=False)
    overall_result: Mapped[str] = mapped_column(String(64), nullable=False)
    reported_at: Mapped[str] = mapped_column(String(64), nullable=False)
    workspace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    diagnostics: Mapped[list[ValidationDiagnostic]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class ValidationDiagnostic(Base):
    __tablename__ = "validation_diagnostic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("validation_run.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    element_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source: Mapped[str | None] = mapped_column(String(512), nullable=True)
    line: Mapped[int | None] = mapped_column(nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    run: Mapped[ValidationRun] = relationship(back_populates="diagnostics")


class GenerationJob(Base):
    __tablename__ = "generation_job"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("workspace.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    implementation_id: Mapped[str] = mapped_column(String(256), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(256), unique=True, nullable=True
    )
    payload_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    result_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    artifacts: Mapped[list[GeneratedArtifact]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class GeneratedArtifact(Base):
    __tablename__ = "generated_artifact"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("generation_job.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    path_or_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    content_digest: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    job: Mapped[GenerationJob] = relationship(back_populates="artifacts")


class ModelIndex(Base):
    __tablename__ = "model_index"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    implementation_id: Mapped[str] = mapped_column(String(256), nullable=False)
    revision: Mapped[str] = mapped_column(String(128), nullable=False)
    content_digest: Mapped[str] = mapped_column(String(128), nullable=False)
    indexed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    elements: Mapped[list[ModelElementIndex]] = relationship(
        back_populates="index", cascade="all, delete-orphan"
    )


class ModelElementIndex(Base):
    __tablename__ = "model_element_index"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    index_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("model_index.id"), nullable=False
    )
    element_id: Mapped[str] = mapped_column(String(256), nullable=False)
    element_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    layer: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    index: Mapped[ModelIndex] = relationship(back_populates="elements")


class AuditEvent(Base):
    __tablename__ = "audit_event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class PublicationRequest(Base):
    __tablename__ = "publication_request"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("workspace.id"), nullable=False
    )
    implementation_id: Mapped[str] = mapped_column(String(256), nullable=False)
    doc_key: Mapped[str] = mapped_column(String(64), nullable=False, default="trading")
    branch_name: Mapped[str] = mapped_column(String(256), nullable=False)
    base_revision: Mapped[str] = mapped_column(String(128), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    review_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    review_id: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    idempotency_key: Mapped[str | None] = mapped_column(
        String(256), unique=True, nullable=True
    )
    payload_fingerprint: Mapped[str] = mapped_column(
        String(128), nullable=False, default=""
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
