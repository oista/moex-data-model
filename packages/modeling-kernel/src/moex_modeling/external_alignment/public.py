"""External Specification Scope and Term Selection — DTOs (ADR-020)."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExternalSpecificationKind(str, Enum):
    ONTOLOGY = "ontology"
    API_SPECIFICATION = "api-specification"
    SCHEMA = "schema"
    DATA_CONTRACT_STANDARD = "data-contract-standard"
    REFERENCE_DATA_STANDARD = "reference-data-standard"
    OTHER = "other"


class ExternalSpecificationAreaKind(str, Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    MODULE = "module"
    ONTOLOGY = "ontology"
    NAMESPACE = "namespace"
    PACKAGE = "package"
    TAG = "tag"
    OTHER = "other"


class ExternalTermKind(str, Enum):
    OWL_CLASS = "owl-class"
    OBJECT_PROPERTY = "object-property"
    DATATYPE_PROPERTY = "datatype-property"
    ANNOTATION_PROPERTY = "annotation-property"
    INDIVIDUAL = "individual"
    API_OPERATION = "api-operation"
    SCHEMA = "schema"
    SCHEMA_PROPERTY = "schema-property"
    ENUM_VALUE = "enum-value"
    GLOSSARY_TERM = "glossary-term"
    OTHER = "other"


class ExternalSelectionDecision(str, Enum):
    CANDIDATE = "candidate"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    DEPRECATED = "deprecated"


class ExtractionRole(str, Enum):
    SEED = "seed"
    DEPENDENCY = "dependency"
    REFERENCE_ONLY = "reference-only"


class ExternalMappingRelation(str, Enum):
    SKOS_EXACT = "skos:exactMatch"
    SKOS_CLOSE = "skos:closeMatch"
    SKOS_BROAD = "skos:broadMatch"
    SKOS_NARROW = "skos:narrowMatch"
    RDFS_SUBCLASS = "rdfs:subClassOf"
    RDFS_SUBPROPERTY = "rdfs:subPropertyOf"
    OWL_EQ_CLASS = "owl:equivalentClass"
    OWL_EQ_PROPERTY = "owl:equivalentProperty"
    NO_MAPPING = "no-mapping"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


_EQUIVALENCE_RELATIONS = frozenset(
    {
        ExternalMappingRelation.OWL_EQ_CLASS,
        ExternalMappingRelation.OWL_EQ_PROPERTY,
    }
)


class UpstreamLocator(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    repository_url: str | None = None
    release_ref: str | None = None
    license_url: str | None = None


class ExternalSpecificationVersion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    title: str | None = None
    description: str | None = None
    name: str | None = None
    external_specification_ref: str
    release_ref: str | None = None
    modeling_standard_ref: str | None = None
    specification_kind: ExternalSpecificationKind | None = None
    upstream: UpstreamLocator | None = None
    status: str | None = None


class ExternalSpecificationArea(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
        populate_by_name=True,
    )

    area_kind: ExternalSpecificationAreaKind | None = Field(
        default=None, alias="kind"
    )
    code: str
    title: str | None = None
    relevance: str | None = None
    rationale: str | None = None


class ExternalSpecificationScope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    title: str | None = None
    description: str | None = None
    external_specification_ref: str
    status: str | None = None
    purpose: str | None = None
    domain_context_refs: tuple[str, ...] = ()
    business_capabilities: tuple[str, ...] = ()
    included_areas: tuple[ExternalSpecificationArea, ...] = ()
    excluded_areas: tuple[ExternalSpecificationArea, ...] = ()
    local_concept_refs: tuple[str, ...] = ()
    owner: str | None = None
    draft_only: bool = False


class SelectionBasis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    use_case: str | None = None
    domain_context_ref: str | None = None
    external_specification_ref: str | None = None


class CompetencyQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    question: str
    use_case: str | None = None
    status: str | None = None


class SelectionRules(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    default_mapping_relation: ExternalMappingRelation = (
        ExternalMappingRelation.SKOS_CLOSE
    )
    owl_equivalent_class_requires_approval: bool = True
    require_rationale_for_accepted_term: bool = True
    require_competency_question_link: bool = True
    maximum_seed_terms: int | None = 25


class ExtractionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    tool: str | None = None
    method: str | None = None
    source_version_ref: str | None = None
    seed_path: str | None = None
    output_path: str | None = None
    output_status: str | None = None
    notes: str | None = None


class MaterializedExternalModule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    path: str | None = None
    status: str | None = None
    content_hash: str | None = None
    extraction_plan_ref: str | None = None


class ExternalMappingAssertion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    local_concept_ref: str | None = None
    upstream_iri: str
    relation: ExternalMappingRelation
    rationale: str | None = None
    confidence: float | None = None
    review_status: ReviewStatus = ReviewStatus.PENDING
    selection_item_ref: str | None = None


class ExternalTermSelectionItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    upstream_iri: str
    term_kind: ExternalTermKind
    upstream_module_ref: str | None = None
    preferred_label: str | None = None
    local_concept_ref: str | None = None
    candidate_relation: ExternalMappingRelation | None = None
    extraction_role: ExtractionRole
    decision: ExternalSelectionDecision
    supports: tuple[str, ...] = ()
    rationale: str | None = None
    review_status: ReviewStatus
    confidence: float | None = None
    draft_only: bool = False


class ExternalTermSelection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    title: str | None = None
    description: str | None = None
    version: str | None = None
    scope_ref: str
    status: str | None = None
    draft_only: bool = False
    selection_basis: SelectionBasis | None = None
    competency_questions: tuple[CompetencyQuestion, ...] = ()
    selected_terms: tuple[ExternalTermSelectionItem, ...] = ()
    selection_rules: SelectionRules | None = None
    extraction_plan: ExtractionPlan | None = None
    materialized_modules: tuple[MaterializedExternalModule, ...] = ()
    mappings: tuple[ExternalMappingAssertion, ...] = ()
    owner: str | None = None


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    severity: str  # error | warning
    code: str
    message: str


class SelectionValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    ok: bool
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "warning")


def _version_token(ref: str) -> str | None:
    """Extract version part from refs like fibo@2026Q2."""
    if "@" in ref:
        return ref.split("@", 1)[1].strip() or None
    return None


def _spec_id_token(ref: str) -> str:
    return ref.split("@", 1)[0].strip()


def validate_scope(scope: ExternalSpecificationScope) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    included = {a.code for a in scope.included_areas}
    excluded = {a.code for a in scope.excluded_areas}
    overlap = included & excluded
    if overlap:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SCOPE-AREA-OVERLAP",
                message=(
                    f"included_areas and excluded_areas share codes: "
                    f"{', '.join(sorted(overlap))}"
                ),
            )
        )
    return issues


def validate_selection(
    selection: ExternalTermSelection,
    *,
    scope: ExternalSpecificationScope | None = None,
    known_scope_ids: set[str] | None = None,
) -> SelectionValidationReport:
    """Enforce ADR-020 invariants 1–10. Returns errors and warnings."""
    issues: list[ValidationIssue] = []
    rules = selection.selection_rules or SelectionRules()
    cq_ids = {q.id for q in selection.competency_questions}
    draft = bool(selection.draft_only) or (
        (selection.status or "").lower() in {"draft", "candidate"}
    )

    # 1. scope_ref must exist when known set / scope provided
    if known_scope_ids is not None and selection.scope_ref not in known_scope_ids:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SEL-SCOPE-MISSING",
                message=f"scope_ref '{selection.scope_ref}' not found",
            )
        )
    if scope is not None and selection.scope_ref != scope.id:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SEL-SCOPE-MISMATCH",
                message=(
                    f"scope_ref '{selection.scope_ref}' does not match "
                    f"loaded scope id '{scope.id}'"
                ),
            )
        )

    # 2. version compatibility with scope
    if scope is not None:
        sel_ver = None
        if selection.selection_basis and selection.selection_basis.external_specification_ref:
            sel_ver = _version_token(
                selection.selection_basis.external_specification_ref
            )
        scope_ver = _version_token(scope.external_specification_ref)
        if sel_ver and scope_ver and sel_ver != scope_ver:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SEL-VERSION-INCOMPATIBLE",
                    message=(
                        f"selection version '{sel_ver}' incompatible with "
                        f"scope version '{scope_ver}'"
                    ),
                ),
            )
        sel_spec = None
        if selection.selection_basis and selection.selection_basis.external_specification_ref:
            sel_spec = _spec_id_token(
                selection.selection_basis.external_specification_ref
            )
        scope_spec = _spec_id_token(scope.external_specification_ref)
        if sel_spec and scope_spec and sel_spec != scope_spec:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="SEL-SPEC-INCOMPATIBLE",
                    message=(
                        f"selection spec '{sel_spec}' incompatible with "
                        f"scope spec '{scope_spec}'"
                    ),
                ),
            )

    if not selection.competency_questions:
        issues.append(
            ValidationIssue(
                severity="error",
                code="SEL-CQ-REQUIRED",
                message="ExternalTermSelection requires at least one competency question",
            )
        )

    seed_count = 0
    for term in selection.selected_terms:
        # 3. required fields
        if not term.upstream_iri:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TERM-IRI-REQUIRED",
                    message=f"term '{term.id}': upstream_iri required",
                )
            )
        if not term.supports:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TERM-CQ-REQUIRED",
                    message=f"term '{term.id}': at least one supports CQ ref required",
                )
            )
        else:
            for cq in term.supports:
                if cq not in cq_ids:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="TERM-CQ-UNKNOWN",
                            message=f"term '{term.id}': unknown CQ '{cq}'",
                        )
                    )

        # 4. accepted requirements
        if term.decision == ExternalSelectionDecision.ACCEPTED:
            if rules.require_rationale_for_accepted_term and not (
                term.rationale and term.rationale.strip()
            ):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TERM-ACCEPTED-RATIONALE",
                        message=f"term '{term.id}': accepted requires rationale",
                    )
                )
            if not term.local_concept_ref and (
                term.candidate_relation != ExternalMappingRelation.NO_MAPPING
            ):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TERM-ACCEPTED-TARGET",
                        message=(
                            f"term '{term.id}': accepted requires local_concept_ref "
                            f"or candidate_relation no-mapping"
                        ),
                    )
                )
            if term.candidate_relation is None:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TERM-ACCEPTED-RELATION",
                        message=f"term '{term.id}': accepted requires candidate_relation",
                    )
                )
            if term.review_status not in {
                ReviewStatus.APPROVED,
                ReviewStatus.PENDING,
            }:
                # accepted may still be pending review, but rejected review is wrong
                if term.review_status == ReviewStatus.REJECTED:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="TERM-ACCEPTED-REVIEW",
                            message=(
                                f"term '{term.id}': accepted incompatible with "
                                f"review_status rejected"
                            ),
                        )
                    )

        # 5. equivalence requires approved
        if (
            term.candidate_relation in _EQUIVALENCE_RELATIONS
            and term.review_status != ReviewStatus.APPROVED
        ):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TERM-EQ-NEEDS-APPROVAL",
                    message=(
                        f"term '{term.id}': {term.candidate_relation.value} "
                        f"forbidden unless review_status=approved"
                    ),
                )
            )

        # 6. seed role
        if term.extraction_role == ExtractionRole.SEED:
            seed_count += 1
            ok_prod = (
                term.decision == ExternalSelectionDecision.ACCEPTED
                and term.review_status == ReviewStatus.APPROVED
            )
            if not draft:
                if not ok_prod:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            code="TERM-SEED-PROD",
                            message=(
                                f"term '{term.id}': production seed requires "
                                f"accepted + approved"
                            ),
                        )
                    )
            else:
                if not ok_prod:
                    if not (selection.draft_only or term.draft_only):
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                code="TERM-SEED-DRAFT-FLAG",
                                message=(
                                    f"term '{term.id}': draft seed for candidate "
                                    f"requires draft_only: true on selection or term"
                                ),
                            )
                        )
                    else:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                code="TERM-SEED-DRAFT",
                                message=(
                                    f"term '{term.id}': draft seed with "
                                    f"decision={term.decision.value}"
                                ),
                            )
                        )

    # 9. maximum_seed_terms warning
    max_seed = rules.maximum_seed_terms
    if max_seed is not None and seed_count > max_seed:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="SEL-MAX-SEED",
                message=f"seed terms {seed_count} exceed maximum_seed_terms {max_seed}",
            )
        )

    # mappings: equivalence needs approved; non-accepted not confirmed
    for m in selection.mappings:
        if (
            m.relation in _EQUIVALENCE_RELATIONS
            and m.review_status != ReviewStatus.APPROVED
        ):
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="MAP-EQ-NEEDS-APPROVAL",
                    message=(
                        f"mapping '{m.id}': {m.relation.value} forbidden unless approved"
                    ),
                )
            )
        if m.relation == ExternalMappingRelation.NO_MAPPING and not (
            m.rationale and m.rationale.strip()
        ):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="MAP-NO-MAPPING-RATIONALE",
                    message=f"mapping '{m.id}': no-mapping should include rationale",
                )
            )

    # 8. materialization only with selection + plan (informational if modules without plan)
    if selection.materialized_modules and selection.extraction_plan is None:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="SEL-MODULE-WITHOUT-PLAN",
                message="materialized_modules present without extraction_plan",
            )
        )

    if scope is not None:
        issues.extend(validate_scope(scope))

    ok = not any(i.severity == "error" for i in issues)
    return SelectionValidationReport(ok=ok, issues=tuple(issues))


def selection_from_dict(data: dict[str, Any]) -> ExternalTermSelection:
    return ExternalTermSelection.model_validate(data)


def scope_from_dict(data: dict[str, Any]) -> ExternalSpecificationScope:
    return ExternalSpecificationScope.model_validate(data)
