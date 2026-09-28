"""Conformance rule registration and execution by phase."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from moex_modeling import ConformancePhase, Diagnostic
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.application.repository import DamsAssetRepository
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
    """Register LinkML validate + DAMS structural/reference rules."""

    def run_linkml(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
        return repo.validate_standard(body)

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
    )
