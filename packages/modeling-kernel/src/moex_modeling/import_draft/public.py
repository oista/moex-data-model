"""ImportDraftEngine port — schema-automator drafts only (ADR-009)."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from moex_modeling.conformance.domain import Diagnostic


class ImportSourceType(str, Enum):
    JSON_SCHEMA = "json_schema"
    SQL = "sql"
    CSV = "csv"
    RDF = "rdf"


GENERATED_DRAFT_STATUS = "generated-draft"


class ImportJobManifest(BaseModel):
    """Audit record for an isolated import job. Never auto-published."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    job_id: str
    status: str = GENERATED_DRAFT_STATUS
    source_type: ImportSourceType
    source_path: str
    source_digest: str
    params: dict[str, Any] = Field(default_factory=dict)
    inferred_schema_path: str | None = None
    diagnostics: tuple[Diagnostic, ...] = ()
    repro_command: str
    created_at: str | None = None


@runtime_checkable
class ImportDraftEngine(Protocol):
    """
    Bootstraps foreign schemas into generated-draft status only.

    Must persist source file + job params for reproducible re-import.
    """

    def run_import(
        self,
        source_path: Path,
        source_type: ImportSourceType | str,
        out_dir: Path,
        *,
        options: dict[str, Any] | None = None,
    ) -> ImportJobManifest: ...


__all__ = [
    "GENERATED_DRAFT_STATUS",
    "ImportDraftEngine",
    "ImportJobManifest",
    "ImportSourceType",
]
