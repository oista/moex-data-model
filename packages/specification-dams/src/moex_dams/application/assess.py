"""Vertical-slice conformance: LinkML validate → DAMS rules → report + graph."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from moex_modeling import (
    ConformanceAssessment,
    ConformancePhase,
    ConformanceReport,
    ConformanceResult,
    Diagnostic,
    ImplementationRef,
    LifecycleStatus,
    ModelUniverse,
    ModelingStandard,
    RelationKind,
    ReferenceSpecification,
    SpecificationImplementation,
    SpecificationKind,
    SpecificationRef,
    StandardFamily,
    StandardRef,
    SourceDescriptor,
    TypedRelation,
    summarize_result,
)
from moex_standard_linkml.domain.body import (
    LinkMLImplementationBody,
    LinkMLSpecificationBody,
)
from moex_standard_linkml.provider import LinkMLStandardProvider

from moex_dams.domain.graph import DamsModelGraphView
from moex_dams.mappings.dams_to_graph import build_dams_graph
from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural

LINKML_STANDARD_ID = "moex:standard:linkml"
DAMS_SPEC_ID = "moex:spec:dams"
DAMS_VERSION = "0.1.0"


@dataclass(frozen=True)
class SliceResult:
    report: ConformanceReport
    universe: ModelUniverse
    graph: DamsModelGraphView
    specification_body: LinkMLSpecificationBody
    implementation_body: LinkMLImplementationBody
    implementation: SpecificationImplementation


def assess_implementation(
    *,
    schema_path: Path | str,
    implementation_path: Path | str,
    implementation_id: str | None = None,
) -> SliceResult:
    schema_path = Path(schema_path)
    implementation_path = Path(implementation_path)
    provider = LinkMLStandardProvider(
        default_schema_path=schema_path,
        default_target_class="ModelPackage",
    )

    spec_ref = SpecificationRef(
        specification_id=DAMS_SPEC_ID,
        specification_version=DAMS_VERSION,
        specification_revision=DAMS_VERSION,
    )
    package_bytes = implementation_path.read_bytes()
    digest = "sha256:" + hashlib.sha256(package_bytes).hexdigest()
    revision = digest.removeprefix("sha256:")[:12]
    impl_id = implementation_id or f"moex:implementation:{implementation_path.stem}"

    impl_ref = ImplementationRef(
        implementation_id=impl_id,
        implementation_revision=revision,
    )

    spec_body = provider.load_specification_body(spec_ref, path=str(schema_path))
    impl_body = provider.load_implementation_body(impl_ref, path=str(implementation_path))

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    standard_ref = StandardRef(
        standard_id=LINKML_STANDARD_ID,
        version_constraint=">=1.7,<2.0",
        standard_revision="1.x",
    )

    linkml_diags = provider.validate_standard(impl_body)
    structural_diags = check_structural(impl_body)
    reference_diags = check_references(impl_body)
    all_diags = linkml_diags + structural_diags + reference_diags

    assessments = (
        _assessment(
            "assessment:standard-syntax",
            impl_ref,
            spec_ref,
            standard_ref,
            linkml_diags,
            now,
            phase=ConformancePhase.STANDARD_SYNTAX,
        ),
        _assessment(
            "assessment:corporate-semantics",
            impl_ref,
            spec_ref,
            standard_ref,
            structural_diags + reference_diags,
            now,
            phase=ConformancePhase.CORPORATE_SEMANTICS,
        ),
    )
    overall = summarize_result(all_diags)
    report = ConformanceReport(
        id=f"report:{impl_id}:{revision}",
        description="Vertical slice conformance for DAMS ModelPackage",
        assessed_implementation=impl_ref,
        assessed_specification=spec_ref,
        assessed_standard=standard_ref,
        overall_result=overall,
        assessments=assessments,
        reported_at=now,
    )

    version = str(impl_body.data.get("model_version") or "0.0.0")
    implementation = SpecificationImplementation(
        id=impl_id,
        name=str(impl_body.data.get("name") or implementation_path.stem),
        description=impl_body.data.get("description"),
        version=version,
        revision=revision,
        content_digest=digest,
        conforms_to=spec_ref,
        implementation_kind=StandardFamily.LINKML,
        lifecycle_status=_lifecycle(impl_body.data.get("lifecycle_status")),
        source=SourceDescriptor(
            source_uri=implementation_path.resolve().as_uri(),
            media_type="application/yaml",
            source_root_type="ModelPackage",
            authoritative=True,
        ),
        body_ref=implementation_path.name,
    )

    standard = ModelingStandard(
        id=LINKML_STANDARD_ID,
        name="linkml",
        version="1.8",
        revision="1.x",
        content_digest="sha256:linkml-placeholder",
        standard_family=StandardFamily.LINKML,
        specification_uri="https://w3id.org/linkml/",
        semantic_regime="closed_world",
    )
    specification = ReferenceSpecification(
        id=DAMS_SPEC_ID,
        name="moex-dams",
        version=DAMS_VERSION,
        revision=DAMS_VERSION,
        content_digest="sha256:" + hashlib.sha256(schema_path.read_bytes()).hexdigest(),
        specification_kind=SpecificationKind.DATA_MODEL,
        expressed_in=standard_ref,
        root_type=spec_body.root_class or "MOEXModelRepository",
        normative_sources=(str(schema_path.resolve()),),
    )

    solution_ref = impl_body.data.get("solution_ref")
    relations: list[TypedRelation] = [
        TypedRelation(
            relation_kind=RelationKind.EXPRESSED_IN,
            relation_source=specification.id,
            relation_target=standard.id,
        ),
        TypedRelation(
            relation_kind=RelationKind.CONFORMS_TO,
            relation_source=implementation.id,
            relation_target=specification.id,
        ),
    ]
    if solution_ref:
        relations.append(
            TypedRelation(
                relation_kind=RelationKind.IMPLEMENTS,
                relation_source=implementation.id,
                relation_target=str(solution_ref),
            )
        )

    universe = ModelUniverse(
        standards=(standard,),
        specifications=(specification,),
        implementations=(implementation,),
        assessments=assessments,
        reports=(report,),
        relations=tuple(relations),
    )
    graph = build_dams_graph(impl_body)

    return SliceResult(
        report=report,
        universe=universe,
        graph=graph,
        specification_body=spec_body,
        implementation_body=impl_body,
        implementation=implementation,
    )


def _assessment(
    assessment_id: str,
    impl_ref: ImplementationRef,
    spec_ref: SpecificationRef,
    standard_ref: StandardRef,
    diagnostics: tuple[Diagnostic, ...],
    assessed_at: str,
    *,
    phase: ConformancePhase,
) -> ConformanceAssessment:
    _ = phase
    return ConformanceAssessment(
        id=assessment_id,
        assessed_implementation=impl_ref,
        assessed_specification=spec_ref,
        assessed_standard=standard_ref,
        conformance_result=summarize_result(diagnostics),
        diagnostics=diagnostics,
        assessed_at=assessed_at,
    )


def _lifecycle(raw: object) -> LifecycleStatus:
    if isinstance(raw, str):
        try:
            return LifecycleStatus(raw)
        except ValueError:
            pass
    return LifecycleStatus.DRAFT
