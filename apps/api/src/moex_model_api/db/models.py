"""SQLAlchemy ORM models for operational tables (adapter layer only)."""

from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Workspace(Base):
    __tablename__ = "workspace"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
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
    run: Mapped[ValidationRun] = relationship(back_populates="diagnostics")


class AuditEvent(Base):
    __tablename__ = "audit_event"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False, default="dev")
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
