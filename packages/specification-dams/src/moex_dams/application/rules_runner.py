"""Conformance rule registration and execution by phase."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from moex_modeling import ConformancePhase, Diagnostic
from moex_standard_linkml.domain.body import LinkMLImplementationBody


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
