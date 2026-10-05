"""Semantic diff envelopes — classification of model changes."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict

from moex_modeling.shared.types import DiagnosticDetail


class ChangeCategory(str, Enum):
    BACKWARD_COMPATIBLE = "backward_compatible"
    BREAKING = "breaking"
    GOVERNANCE = "governance"
    OPERATIONAL = "operational"
    NON_BREAKING = "non_breaking"
    DEPRECATION = "deprecation"


class SemanticChange(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    change_code: str
    category: ChangeCategory
    subject_ref: str | None = None
    message: str
    path: str | None = None
    before: tuple[DiagnosticDetail, ...] = ()
    after: tuple[DiagnosticDetail, ...] = ()


class SemanticDiffReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    base_label: str
    target_label: str
    changes: tuple[SemanticChange, ...] = ()

    @property
    def has_breaking(self) -> bool:
        return any(c.category is ChangeCategory.BREAKING for c in self.changes)

    def counts_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {cat.value: 0 for cat in ChangeCategory}
        for change in self.changes:
            counts[change.category.value] = counts.get(change.category.value, 0) + 1
        return counts
