"""Conformance rule registration and execution by phase."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from moex_modeling import ConformancePhase, Diagnostic
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.application.repository import DamsAssetRepository
from moex_dams.rules.dams_levels import check_dams_model_level
from moex_dams.rules.identifiers import build_dams_curie_resolver, check_identifiers
from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural


@dataclass(frozen=True)
class RuleSet:
    phase: ConformancePhase
    assessment_id: str
    description: str
    run: Callable[[LinkMLImplementationBody], tuple[Diagnostic, ...]]


def run_rule_sets(
    body: LinkMLImplementationBody,
    sets: Sequence[RuleSet],
) -> list[tuple[RuleSet, tuple[Diagnostic, ...]]]:
    return [(rule_set, rule_set.run(body)) for rule_set in sets]


def default_dams_rule_sets(repo: DamsAssetRepository) -> tuple[RuleSet, ...]:
    """Register LinkML validate + DAMS structural/reference/identifier rules."""

    def run_linkml(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
        return repo.validate_standard(body)

    resolver = None
    if repo.default_schema_path is not None:
        resolver = build_dams_curie_resolver(repo.default_schema_path)

    def run_identifiers(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
        if resolver is None:
            return ()
        return check_identifiers(body, resolver=resolver)

    return (
        RuleSet(
            phase=ConformancePhase.STANDARD_SYNTAX,
            assessment_id="assessment:standard-syntax",
            description="LinkML standard validation",
            run=run_linkml,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:structural",
            description="DAMS structural rules",
            run=check_structural,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:references",
            description="DAMS reference integrity rules",
            run=check_references,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:identifiers",
            description="CURIE/URI prefix rules",
            run=run_identifiers,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:dams-levels",
            description="DAMS enterprise-conceptual / solution package rules",
            run=check_dams_model_level,
        ),
    )
