"""SchemaAutomatorImportEngine — draft-only imports (ADR-009)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.import_draft.public import (
    GENERATED_DRAFT_STATUS,
    ImportJobManifest,
    ImportSourceType,
)
from moex_modeling.shared.enums import DiagnosticSeverity


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def _lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _dump_schema(schema: Any) -> str:
    """Serialize SchemaDefinition-like object to YAML text."""
    if hasattr(schema, "dict"):
        data = schema.dict()
    elif hasattr(schema, "model_dump"):
        data = schema.model_dump(mode="python", exclude_none=True)
    elif isinstance(schema, dict):
        data = schema
    else:
        # linkml SchemaDefinition
        try:
            from linkml_runtime.dumpers import yaml_dumper

            return _lf(yaml_dumper.dumps(schema))
        except Exception:  # noqa: BLE001
            data = {"name": getattr(schema, "name", "inferred"), "raw": str(schema)}
    return _lf(yaml.safe_dump(data, sort_keys=True, allow_unicode=True))


def _unsupported(source_type: ImportSourceType) -> Diagnostic:
    return Diagnostic(
        diagnostic_code="IMPORT-UNSUPPORTED-001",
        severity=DiagnosticSeverity.ERROR,
        diagnostic_message=f"source_type={source_type.value} is not supported in this build",
    )


class SchemaAutomatorImportEngine:
    """Filesystem-backed import jobs under out_dir/<job_id>/."""

    def run_import(
        self,
        source_path: Path,
        source_type: ImportSourceType | str,
        out_dir: Path,
        *,
        options: dict[str, Any] | None = None,
    ) -> ImportJobManifest:
        options = dict(options or {})
        if isinstance(source_type, str):
            source_type = ImportSourceType(source_type)
        source_path = source_path.resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"import source not found: {source_path}")

        job_id = str(options.get("job_id") or uuid.uuid4())
        job_dir = out_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        source_copy = job_dir / f"source{source_path.suffix or '.bin'}"
        shutil.copy2(source_path, source_copy)
        source_digest = _sha256_file(source_copy)

        diagnostics: list[Diagnostic] = []
        inferred_path: Path | None = None
        schema_text: str | None = None

        try:
            schema_text, extra_diags = self._infer(source_copy, source_type, options)
            diagnostics.extend(extra_diags)
        except ImportError as exc:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="IMPORT-DEP-001",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        f"schema-automator required: {exc}; "
                        "install moex-linkml-tooling[automator]"
                    ),
                )
            )
        except (OSError, ValueError, TypeError, RuntimeError) as exc:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="IMPORT-FAIL-001",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=str(exc),
                )
            )

        if schema_text is not None:
            inferred_path = job_dir / "inferred-schema.yaml"
            inferred_path.write_text(schema_text, encoding="utf-8", newline="\n")
            # Uncertainty heuristics
            if "range: string" in schema_text and source_type == ImportSourceType.JSON_SCHEMA:
                diagnostics.append(
                    Diagnostic(
                        diagnostic_code="IMPORT-UNCERTAIN-001",
                        severity=DiagnosticSeverity.WARNING,
                        diagnostic_message=(
                            "inferred schema uses string ranges; "
                            "architect should refine types and descriptions"
                        ),
                    )
                )

        diag_path = job_dir / "diagnostics.json"
        diag_path.write_text(
            json.dumps(
                [d.model_dump(mode="json") for d in diagnostics],
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        repro = (
            f"moex-model import --source-type {source_type.value} "
            f"--source {source_path} --out {out_dir}"
        )
        created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = ImportJobManifest(
            job_id=job_id,
            status=GENERATED_DRAFT_STATUS,
            source_type=source_type,
            source_path=str(source_copy.relative_to(job_dir)),
            source_digest=source_digest,
            params={
                "source_type": source_type.value,
                "original_source": str(source_path),
                **{k: v for k, v in options.items() if k != "job_id"},
            },
            inferred_schema_path=(
                str(inferred_path.relative_to(job_dir)) if inferred_path else None
            ),
            diagnostics=tuple(diagnostics),
            repro_command=repro,
            created_at=created,
        )
        (job_dir / "job.json").write_text(
            manifest.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return manifest

    def _infer(
        self,
        source_copy: Path,
        source_type: ImportSourceType,
        options: dict[str, Any],
    ) -> tuple[str | None, list[Diagnostic]]:
        name = str(options.get("name") or source_copy.stem)
        if source_type == ImportSourceType.JSON_SCHEMA:
            from schema_automator.importers.jsonschema_import_engine import (
                JsonSchemaImportEngine,
            )

            engine = JsonSchemaImportEngine()
            schema = engine.convert(str(source_copy), name=name, format="json")
            return _dump_schema(schema), []

        if source_type == ImportSourceType.SQL:
            return self._infer_sql(source_copy, name)

        if source_type == ImportSourceType.CSV:
            try:
                from schema_automator.importers.tabular_import_engine import (
                    TabularImportEngine,
                )
            except ImportError:
                return None, [_unsupported(source_type)]
            engine = TabularImportEngine()
            # API varies; try common convert(path)
            if hasattr(engine, "convert"):
                schema = engine.convert(str(source_copy), name=name)
                return _dump_schema(schema), []
            return None, [_unsupported(source_type)]

        if source_type == ImportSourceType.RDF:
            try:
                from schema_automator.importers.owl_import_engine import OwlImportEngine
            except ImportError:
                return None, [_unsupported(source_type)]
            engine = OwlImportEngine()
            schema = engine.convert(str(source_copy), name=name)
            return _dump_schema(schema), []

        return None, [_unsupported(source_type)]

    def _infer_sql(
        self, source_copy: Path, name: str
    ) -> tuple[str | None, list[Diagnostic]]:
        from schema_automator.importers.sql_import_engine import SqlImportEngine

        text = source_copy.read_text(encoding="utf-8")
        # If already sqlite, use directly; else apply DDL into temp sqlite.
        if source_copy.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
            db_path = source_copy
            cleanup: Path | None = None
        else:
            cleanup = Path(tempfile.mkdtemp()) / "import.sqlite"
            conn = sqlite3.connect(str(cleanup))
            try:
                conn.executescript(text)
                conn.commit()
            finally:
                conn.close()
            db_path = cleanup

        try:
            engine = SqlImportEngine()
            schema = engine.convert(str(db_path), name=name)
            return _dump_schema(schema), []
        finally:
            if cleanup is not None:
                try:
                    cleanup.unlink(missing_ok=True)
                    cleanup.parent.rmdir()
                except OSError:
                    pass


__all__ = ["SchemaAutomatorImportEngine"]
