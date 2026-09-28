"""ADR-020 external alignment validation invariants."""

from __future__ import annotations

from moex_modeling.external_alignment.public import (
    CompetencyQuestion,
    ExternalMappingAssertion,
    ExternalMappingRelation,
    ExternalSelectionDecision,
    ExternalSpecificationArea,
    ExternalSpecificationScope,
    ExternalTermKind,
    ExternalTermSelection,
    ExternalTermSelectionItem,
    ExtractionRole,
    ReviewStatus,
    SelectionBasis,
    SelectionRules,
    validate_scope,
    validate_selection,
)


def _cq() -> tuple[CompetencyQuestion, ...]:
    return (
        CompetencyQuestion(id="CQ-1", question="Who is the participant?"),
        CompetencyQuestion(id="CQ-2", question="What identifiers exist?"),
    )


def _base_selection(**kwargs) -> ExternalTermSelection:
    data = dict(
        id="sel-1",
        scope_ref="scope-1",
        draft_only=True,
        status="draft",
        selection_basis=SelectionBasis(
            use_case="onboarding",
            domain_context_ref="participant-and-admission",
            external_specification_ref="fibo@2026Q2",
        ),
        competency_questions=_cq(),
        selected_terms=(),
        selection_rules=SelectionRules(maximum_seed_terms=25),
    )
    data.update(kwargs)
    return ExternalTermSelection(**data)


def _scope(**kwargs) -> ExternalSpecificationScope:
    data = dict(
        id="scope-1",
        external_specification_ref="fibo@2026Q2",
        status="draft",
        included_areas=(
            ExternalSpecificationArea(kind="domain", code="FND", title="Foundations"),
            ExternalSpecificationArea(kind="domain", code="BE", title="Business Entities"),
        ),
        excluded_areas=(
            ExternalSpecificationArea(code="SEC", rationale="deferred"),
        ),
    )
    data.update(kwargs)
    return ExternalSpecificationScope(**data)


def test_scope_area_overlap_error():
    scope = _scope(
        excluded_areas=(ExternalSpecificationArea(code="FND", rationale="x"),)
    )
    issues = validate_scope(scope)
    assert any(i.code == "SCOPE-AREA-OVERLAP" for i in issues)


def test_scope_ref_must_exist():
    sel = _base_selection(scope_ref="missing")
    report = validate_selection(sel, known_scope_ids={"scope-1"})
    assert not report.ok
    assert any(i.code == "SEL-SCOPE-MISSING" for i in report.errors)


def test_version_compatibility():
    scope = _scope(external_specification_ref="fibo@2025Q4")
    sel = _base_selection()
    report = validate_selection(sel, scope=scope)
    assert any(i.code == "SEL-VERSION-INCOMPATIBLE" for i in report.errors)


def test_term_requires_supports_and_fields():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://example.org/T",
        term_kind=ExternalTermKind.OWL_CLASS,
        extraction_role=ExtractionRole.REFERENCE_ONLY,
        decision=ExternalSelectionDecision.CANDIDATE,
        supports=(),
        review_status=ReviewStatus.PENDING,
        draft_only=True,
    )
    sel = _base_selection(selected_terms=(term,))
    report = validate_selection(sel, scope=_scope())
    assert any(i.code == "TERM-CQ-REQUIRED" for i in report.errors)


def test_accepted_requires_rationale_relation_target():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://example.org/T",
        term_kind=ExternalTermKind.OWL_CLASS,
        extraction_role=ExtractionRole.DEPENDENCY,
        decision=ExternalSelectionDecision.ACCEPTED,
        supports=("CQ-1",),
        review_status=ReviewStatus.PENDING,
    )
    sel = _base_selection(selected_terms=(term,), draft_only=True)
    report = validate_selection(sel, scope=_scope())
    codes = {i.code for i in report.errors}
    assert "TERM-ACCEPTED-RATIONALE" in codes
    assert "TERM-ACCEPTED-TARGET" in codes
    assert "TERM-ACCEPTED-RELATION" in codes


def test_owl_equivalent_requires_approved():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://example.org/T",
        term_kind=ExternalTermKind.OWL_CLASS,
        local_concept_ref="moex:LegalEntity",
        candidate_relation=ExternalMappingRelation.OWL_EQ_CLASS,
        extraction_role=ExtractionRole.DEPENDENCY,
        decision=ExternalSelectionDecision.ACCEPTED,
        supports=("CQ-1",),
        rationale="strong match",
        review_status=ReviewStatus.PENDING,
    )
    sel = _base_selection(selected_terms=(term,))
    report = validate_selection(sel, scope=_scope())
    assert any(i.code == "TERM-EQ-NEEDS-APPROVAL" for i in report.errors)


def test_draft_seed_candidate_warns_with_draft_only():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://example.org/T",
        term_kind=ExternalTermKind.OWL_CLASS,
        extraction_role=ExtractionRole.SEED,
        decision=ExternalSelectionDecision.CANDIDATE,
        supports=("CQ-1",),
        review_status=ReviewStatus.PENDING,
        draft_only=True,
    )
    sel = _base_selection(selected_terms=(term,), draft_only=True)
    report = validate_selection(sel, scope=_scope())
    assert report.ok
    assert any(i.code == "TERM-SEED-DRAFT" for i in report.warnings)


def test_production_seed_requires_accepted_approved():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://example.org/T",
        term_kind=ExternalTermKind.OWL_CLASS,
        local_concept_ref="moex:LegalEntity",
        candidate_relation=ExternalMappingRelation.SKOS_CLOSE,
        extraction_role=ExtractionRole.SEED,
        decision=ExternalSelectionDecision.CANDIDATE,
        supports=("CQ-1",),
        review_status=ReviewStatus.PENDING,
        rationale="x",
    )
    sel = _base_selection(
        selected_terms=(term,),
        draft_only=False,
        status="published",
    )
    report = validate_selection(sel, scope=_scope())
    assert any(i.code == "TERM-SEED-PROD" for i in report.errors)


def test_maximum_seed_terms_warning():
    terms = []
    for i in range(26):
        terms.append(
            ExternalTermSelectionItem(
                id=f"t{i}",
                upstream_iri=f"https://example.org/T{i}",
                term_kind=ExternalTermKind.OWL_CLASS,
                extraction_role=ExtractionRole.SEED,
                decision=ExternalSelectionDecision.CANDIDATE,
                supports=("CQ-1",),
                review_status=ReviewStatus.PENDING,
                draft_only=True,
            )
        )
    sel = _base_selection(selected_terms=tuple(terms), draft_only=True)
    report = validate_selection(sel, scope=_scope())
    assert any(i.code == "SEL-MAX-SEED" for i in report.warnings)


def test_happy_path_accepted_approved_seed():
    term = ExternalTermSelectionItem(
        id="t1",
        upstream_iri="https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/LegalPerson",
        term_kind=ExternalTermKind.OWL_CLASS,
        preferred_label="Legal Person",
        local_concept_ref="moex:LegalEntity",
        candidate_relation=ExternalMappingRelation.SKOS_CLOSE,
        extraction_role=ExtractionRole.SEED,
        decision=ExternalSelectionDecision.ACCEPTED,
        supports=("CQ-1",),
        rationale="close match to MOEX LegalEntity",
        review_status=ReviewStatus.APPROVED,
    )
    mapping = ExternalMappingAssertion(
        id="m1",
        local_concept_ref="moex:LegalEntity",
        upstream_iri=term.upstream_iri,
        relation=ExternalMappingRelation.SKOS_CLOSE,
        rationale="manual",
        review_status=ReviewStatus.APPROVED,
        selection_item_ref="t1",
    )
    sel = _base_selection(
        selected_terms=(term,),
        mappings=(mapping,),
        draft_only=False,
        status="published",
    )
    report = validate_selection(sel, scope=_scope(), known_scope_ids={"scope-1"})
    assert report.ok
    assert not report.errors
