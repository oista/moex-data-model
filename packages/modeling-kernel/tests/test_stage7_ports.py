"""Shape checks for Stage 7 mapping / import_draft ports."""

from __future__ import annotations

from pathlib import Path

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.import_draft.public import (
    GENERATED_DRAFT_STATUS,
    ImportDraftEngine,
    ImportJobManifest,
    ImportSourceType,
)
from moex_modeling.mapping.public import (
    MappingPreview,
    MappingProvider,
    MappingResult,
    TransformSpecMeta,
)
from moex_modeling.shared.enums import DiagnosticSeverity, TransformationKind


def test_transform_spec_meta_requires_revisions() -> None:
    meta = TransformSpecMeta(
        spec_id="moex:transform:identity:0.1",
        source_schema_revision="dams-0.1",
        target_schema_revision="dams-0.1",
        transformation_kind=TransformationKind.LOSSLESS,
    )
    assert meta.allow_unrestricted_eval is False
    assert meta.source_schema_revision == meta.target_schema_revision


def test_mapping_preview_and_result_shapes() -> None:
    meta = TransformSpecMeta(
        spec_id="t1",
        source_schema_revision="src-1",
        target_schema_revision="tgt-1",
    )
    preview = MappingPreview(
        spec=meta,
        preserved_semantics=("id",),
        lost_semantics=("legacy_code",),
    )
    result = MappingResult(
        spec=meta,
        output={"id": "x"},
        preserved_semantics=("id",),
        lost_semantics=("legacy_code",),
        round_trip_ok=False,
    )
    assert preview.lost_semantics == ("legacy_code",)
    assert result.output["id"] == "x"


def test_import_job_manifest_is_generated_draft() -> None:
    manifest = ImportJobManifest(
        job_id="job-1",
        source_type=ImportSourceType.JSON_SCHEMA,
        source_path="source.json",
        source_digest="sha256:abc",
        repro_command="moex-model import --source-type json_schema --source source.json --out out",
        diagnostics=(
            Diagnostic(
                diagnostic_code="IMPORT-UNCERTAIN-001",
                severity=DiagnosticSeverity.WARNING,
                diagnostic_message="range for slot foo is ambiguous",
            ),
        ),
    )
    assert manifest.status == GENERATED_DRAFT_STATUS
    assert len(manifest.diagnostics) == 1


def test_mapping_provider_protocol_is_runtime_checkable() -> None:
    class Stub:
        def load_spec_meta(self, spec_path: Path) -> TransformSpecMeta:
            return TransformSpecMeta(
                spec_id="s",
                source_schema_revision="a",
                target_schema_revision="b",
            )

        def validate_spec(self, spec_path: Path) -> list[Diagnostic]:
            return []

        def preview(self, spec_path: Path, sample_path: Path) -> MappingPreview:
            return MappingPreview(spec=self.load_spec_meta(spec_path))

        def transform_sample(self, spec_path: Path, sample_path: Path) -> MappingResult:
            return MappingResult(spec=self.load_spec_meta(spec_path))

    assert isinstance(Stub(), MappingProvider)


def test_import_draft_engine_protocol_is_runtime_checkable() -> None:
    class Stub:
        def run_import(
            self,
            source_path: Path,
            source_type: ImportSourceType | str,
            out_dir: Path,
            *,
            options: dict | None = None,
        ) -> ImportJobManifest:
            return ImportJobManifest(
                job_id="j",
                source_type=ImportSourceType.SQL,
                source_path=str(source_path),
                source_digest="sha256:0",
                repro_command="echo",
            )

    assert isinstance(Stub(), ImportDraftEngine)
