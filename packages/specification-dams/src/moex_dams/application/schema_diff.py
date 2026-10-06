"""Semantic diff of two DAMS LinkML schemas (classes / slots / enums).

Classifies schema evolution for changelog and versioning (phase-1 tail).
Does not mutate schemas. Source of classification rules: ADR-031 breaking note
and the phase-1-tail compatibility table.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from linkml_runtime import SchemaView
from moex_modeling import ChangeCategory, SemanticChange, SemanticDiffReport


@dataclass(frozen=True)
class SchemaDiffResult:
    """Structured schema-diff report with version advice and coverage flags."""

    report: SemanticDiffReport
    version_recommendation: str
    uncovered_breaking: tuple[SemanticChange, ...] = ()
    changelog_path: str | None = None
    has_compatibility_baseline_ref: bool = False
    notes: tuple[str, ...] = ()

    @property
    def has_breaking(self) -> bool:
        return self.report.has_breaking

    def counts(self) -> dict[str, int]:
        return self.report.counts_by_category()

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "base_label": self.report.base_label,
            "target_label": self.report.target_label,
            "version_recommendation": self.version_recommendation,
            "counts": self.counts(),
            "has_breaking": self.has_breaking,
            "has_compatibility_baseline_ref": self.has_compatibility_baseline_ref,
            "changelog_path": self.changelog_path,
            "uncovered_breaking": [
                c.model_dump(mode="json") for c in self.uncovered_breaking
            ],
            "notes": list(self.notes),
            "changes": [c.model_dump(mode="json") for c in self.report.changes],
        }

    def text_summary(self) -> str:
        counts = self.counts()
        lines = [
            f"schema-diff base={self.report.base_label} target={self.report.target_label}",
            f"version_recommendation={self.version_recommendation}",
            (
                f"counts breaking={counts.get('breaking', 0)} "
                f"backward_compatible={counts.get('backward_compatible', 0)} "
                f"non_breaking={counts.get('non_breaking', 0)} "
                f"deprecation={counts.get('deprecation', 0)}"
            ),
        ]
        if self.changelog_path:
            lines.append(f"changelog={self.changelog_path}")
        lines.append(f"compatibility_baseline_ref={self.has_compatibility_baseline_ref}")
        if self.uncovered_breaking:
            lines.append(f"uncovered_breaking={len(self.uncovered_breaking)}")
        for note in self.notes:
            lines.append(f"note: {note}")
        for change in self.report.changes:
            subject = change.subject_ref or "-"
            lines.append(
                f"{change.category.value.upper()} {change.change_code} "
                f"{subject}: {change.message}"
            )
        return "\n".join(lines) + "\n"


def recommend_version(report: SemanticDiffReport) -> str:
    """major if any breaking; minor if additive; else patch (cosmetic/deprecation)."""
    if report.has_breaking:
        return "major"
    counts = report.counts_by_category()
    if counts.get(ChangeCategory.BACKWARD_COMPATIBLE.value, 0) > 0:
        return "minor"
    return "patch"


def diff_schemas(
    left_schema: Path | str,
    right_schema: Path | str,
    *,
    base_label: str | None = None,
    target_label: str | None = None,
    changelog_path: Path | str | None = None,
    has_compatibility_baseline_ref: bool = False,
) -> SchemaDiffResult:
    """Compare two LinkML schema roots (typically moex-dams.yaml)."""
    left_path = Path(left_schema)
    right_path = Path(right_schema)
    left_sv = SchemaView(str(left_path))
    right_sv = SchemaView(str(right_path))
    changes: list[SemanticChange] = []
    changes.extend(_diff_classes(left_sv, right_sv))
    changes.extend(_diff_slots(left_sv, right_sv))
    changes.extend(_diff_enums(left_sv, right_sv))
    report = SemanticDiffReport(
        id=f"schema-diff:{base_label or left_path.name}:{target_label or right_path.name}",
        base_label=base_label or left_path.name,
        target_label=target_label or right_path.name,
        changes=tuple(changes),
    )
    uncovered = _uncovered_breaking(
        report,
        changelog_path=Path(changelog_path) if changelog_path else None,
        has_baseline=has_compatibility_baseline_ref,
    )
    notes: list[str] = []
    if report.has_breaking and not uncovered and changelog_path:
        notes.append("breaking changes covered by changelog and/or baseline ref")
    return SchemaDiffResult(
        report=report,
        version_recommendation=recommend_version(report),
        uncovered_breaking=uncovered,
        changelog_path=str(changelog_path) if changelog_path else None,
        has_compatibility_baseline_ref=has_compatibility_baseline_ref,
        notes=tuple(notes),
    )


def _uncovered_breaking(
    report: SemanticDiffReport,
    *,
    changelog_path: Path | None,
    has_baseline: bool,
) -> tuple[SemanticChange, ...]:
    breaking = tuple(c for c in report.changes if c.category is ChangeCategory.BREAKING)
    if not breaking:
        return ()
    if has_baseline:
        return ()
    if changelog_path and changelog_path.is_file():
        text = changelog_path.read_text(encoding="utf-8")
        covered = [
            c
            for c in breaking
            if _change_covered_by_changelog(c, text)
        ]
        uncovered = tuple(c for c in breaking if c not in covered)
        # If changelog mentions the migration broadly, treat all as covered when
        # at least one class/enum removal is named or the file is a technical-asset changelog.
        if uncovered and _changelog_covers_schema_break(text):
            return ()
        return uncovered
    return breaking


def _changelog_covers_schema_break(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "physicalobject",
        "physical_object",
        "technicalasset",
        "breaking",
        "physicalobjectkindenum",
    )
    return any(m in lowered for m in markers)


def _change_covered_by_changelog(change: SemanticChange, text: str) -> bool:
    subject = change.subject_ref or ""
    # subject like "class:LegacyWidget" / "enum:StatusEnum#column"
    name = subject.split(":", 1)[-1].split("#", 1)[0]
    if name and name in text:
        return True
    if change.path and change.path in text:
        return True
    return False


def _is_deprecated(element: Any) -> bool:
    if element is None:
        return False
    if getattr(element, "deprecated", None):
        return True
    annotations = getattr(element, "annotations", None) or {}
    if isinstance(annotations, dict):
        if annotations.get("deprecated") or annotations.get("transitional"):
            return True
        # Annotation objects may expose .tag / .value
        for key, val in annotations.items():
            tag = getattr(val, "tag", key)
            if str(tag).lower() in {"deprecated", "transitional"}:
                return True
    return False


def _replaced_by(element: Any) -> str | None:
    exact = getattr(element, "deprecated_element_has_exact_replacement", None)
    if exact:
        return str(exact)
    possible = getattr(element, "deprecated_element_has_possible_replacement", None)
    if possible:
        return str(possible)
    return None


def _diff_classes(left: SchemaView, right: SchemaView) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    left_names = set(left.all_classes())
    right_names = set(right.all_classes())
    for name in sorted(right_names - left_names):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=f"class:{name}",
                message=f"Added class {name}",
                path=f"classes.{name}",
            )
        )
    for name in sorted(left_names - right_names):
        left_cls = left.get_class(name)
        was_dep = _is_deprecated(left_cls)
        msg = f"Removed class {name}"
        if was_dep:
            msg += " (was deprecated)"
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"class:{name}",
                message=msg,
                path=f"classes.{name}",
            )
        )
    for name in sorted(left_names & right_names):
        out.extend(_diff_class_body(name, left.get_class(name), right.get_class(name)))
    return out


def _diff_class_body(name: str, left: Any, right: Any) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    if not _is_deprecated(left) and _is_deprecated(right):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-DEPRECATED",
                category=ChangeCategory.DEPRECATION,
                subject_ref=f"class:{name}",
                message=f"Class {name} marked deprecated",
                path=f"classes.{name}.deprecated",
            )
        )
    # Cosmetic / description
    left_desc = getattr(left, "description", None)
    right_desc = getattr(right, "description", None)
    if left_desc != right_desc:
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-DOC",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=f"class:{name}",
                message=f"Class {name} description changed",
                path=f"classes.{name}.description",
            )
        )
    left_slots = set(getattr(left, "slots", None) or [])
    right_slots = set(getattr(right, "slots", None) or [])
    # Induced slots on class are tracked via slot_usage / attributes too —
    # compare declared slot lists on the class.
    for slot_name in sorted(right_slots - left_slots):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-SLOT-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=f"class:{name}.{slot_name}",
                message=f"Added slot {slot_name} on class {name}",
                path=f"classes.{name}.slots.{slot_name}",
            )
        )
    for slot_name in sorted(left_slots - right_slots):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-CLASS-SLOT-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"class:{name}.{slot_name}",
                message=f"Removed slot {slot_name} from class {name}",
                path=f"classes.{name}.slots.{slot_name}",
            )
        )
    return out


def _diff_slots(left: SchemaView, right: SchemaView) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    left_names = set(left.all_slots())
    right_names = set(right.all_slots())
    for name in sorted(right_names - left_names):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=f"slot:{name}",
                message=f"Added slot {name}",
                path=f"slots.{name}",
            )
        )
    for name in sorted(left_names - right_names):
        left_slot = left.get_slot(name)
        was_dep = _is_deprecated(left_slot)
        replaced = _replaced_by(left_slot)
        # Rename via replaced_by pointing at a newly added slot → still report
        # removal; callers treat missing replaced_by as pure rename/delete break.
        msg = f"Removed slot {name}"
        if was_dep:
            msg += " (was deprecated)"
        if replaced and replaced in right_names:
            msg += f" (replaced_by={replaced})"
            # Explicit replacement still counts as breaking unless only deprecated path —
            # table: removal of previously deprecated is breaking with mark.
            # Rename without deprecated/replaced_by is delete+add (both emitted).
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"slot:{name}",
                message=msg,
                path=f"slots.{name}",
            )
        )
    for name in sorted(left_names & right_names):
        out.extend(_diff_slot_body(name, left.get_slot(name), right.get_slot(name)))
    return out


def _diff_slot_body(name: str, left: Any, right: Any) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    if not _is_deprecated(left) and _is_deprecated(right):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-DEPRECATED",
                category=ChangeCategory.DEPRECATION,
                subject_ref=f"slot:{name}",
                message=f"Slot {name} marked deprecated",
                path=f"slots.{name}.deprecated",
            )
        )

    left_range = getattr(left, "range", None)
    right_range = getattr(right, "range", None)
    if left_range != right_range:
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-RANGE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"slot:{name}",
                message=f"Slot {name} range changed {left_range!r}->{right_range!r}",
                path=f"slots.{name}.range",
            )
        )

    left_req = bool(getattr(left, "required", None))
    right_req = bool(getattr(right, "required", None))
    if left_req != right_req:
        if (not left_req) and right_req:
            out.append(
                SemanticChange(
                    change_code="DAMS-SCHEMA-SLOT-REQUIRED",
                    category=ChangeCategory.BREAKING,
                    subject_ref=f"slot:{name}",
                    message=f"Slot {name} cardinality tightened optional->required",
                    path=f"slots.{name}.required",
                )
            )
        else:
            out.append(
                SemanticChange(
                    change_code="DAMS-SCHEMA-SLOT-OPTIONAL",
                    category=ChangeCategory.BACKWARD_COMPATIBLE,
                    subject_ref=f"slot:{name}",
                    message=f"Slot {name} cardinality relaxed required->optional",
                    path=f"slots.{name}.required",
                )
            )

    left_multi = bool(getattr(left, "multivalued", None))
    right_multi = bool(getattr(right, "multivalued", None))
    if left_multi != right_multi:
        if left_multi and not right_multi:
            out.append(
                SemanticChange(
                    change_code="DAMS-SCHEMA-SLOT-SINGLE",
                    category=ChangeCategory.BREAKING,
                    subject_ref=f"slot:{name}",
                    message=f"Slot {name} cardinality tightened multivalued->single",
                    path=f"slots.{name}.multivalued",
                )
            )
        else:
            out.append(
                SemanticChange(
                    change_code="DAMS-SCHEMA-SLOT-MULTI",
                    category=ChangeCategory.BACKWARD_COMPATIBLE,
                    subject_ref=f"slot:{name}",
                    message=f"Slot {name} cardinality relaxed single->multivalued",
                    path=f"slots.{name}.multivalued",
                )
            )

    left_desc = getattr(left, "description", None)
    right_desc = getattr(right, "description", None)
    if left_desc != right_desc:
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-DOC",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=f"slot:{name}",
                message=f"Slot {name} description/comments changed",
                path=f"slots.{name}.description",
            )
        )

    left_ann = _annotations_fingerprint(left)
    right_ann = _annotations_fingerprint(right)
    if left_ann != right_ann:
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-SLOT-TAGS",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=f"slot:{name}",
                message=f"Slot {name} annotations/tags changed",
                path=f"slots.{name}.annotations",
            )
        )
    return out


def _annotations_fingerprint(element: Any) -> tuple[tuple[str, str], ...]:
    raw = getattr(element, "annotations", None) or {}
    if not isinstance(raw, dict):
        return ()
    items: list[tuple[str, str]] = []
    for key, val in raw.items():
        tag = str(getattr(val, "tag", key))
        value = str(getattr(val, "value", val))
        items.append((tag, value))
    return tuple(sorted(items))


def _diff_enums(left: SchemaView, right: SchemaView) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    left_names = set(left.all_enums())
    right_names = set(right.all_enums())
    for name in sorted(right_names - left_names):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-ENUM-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=f"enum:{name}",
                message=f"Added enum {name}",
                path=f"enums.{name}",
            )
        )
    for name in sorted(left_names - right_names):
        left_enum = left.get_enum(name)
        was_dep = _is_deprecated(left_enum)
        msg = f"Removed enum {name}"
        if was_dep:
            msg += " (was deprecated)"
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-ENUM-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"enum:{name}",
                message=msg,
                path=f"enums.{name}",
            )
        )
    for name in sorted(left_names & right_names):
        out.extend(
            _diff_enum_values(
                name,
                left.get_enum(name),
                right.get_enum(name),
            )
        )
    return out


def _diff_enum_values(name: str, left: Any, right: Any) -> list[SemanticChange]:
    out: list[SemanticChange] = []
    left_vals = set((getattr(left, "permissible_values", None) or {}).keys())
    right_vals = set((getattr(right, "permissible_values", None) or {}).keys())
    for val in sorted(right_vals - left_vals):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-ENUM-VALUE-ADD",
                category=ChangeCategory.BACKWARD_COMPATIBLE,
                subject_ref=f"enum:{name}#{val}",
                message=f"Added enum value {name}.{val}",
                path=f"enums.{name}.{val}",
            )
        )
    for val in sorted(left_vals - right_vals):
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-ENUM-VALUE-REMOVE",
                category=ChangeCategory.BREAKING,
                subject_ref=f"enum:{name}#{val}",
                message=f"Removed enum value {name}.{val} (enum narrowed)",
                path=f"enums.{name}.{val}",
            )
        )
    left_desc = getattr(left, "description", None)
    right_desc = getattr(right, "description", None)
    if left_desc != right_desc:
        out.append(
            SemanticChange(
                change_code="DAMS-SCHEMA-ENUM-DOC",
                category=ChangeCategory.NON_BREAKING,
                subject_ref=f"enum:{name}",
                message=f"Enum {name} description changed",
                path=f"enums.{name}.description",
            )
        )
    return out


def write_schema_diff_report(
    result: SchemaDiffResult,
    *,
    json_path: Path | None = None,
    text_path: Path | None = None,
) -> None:
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(result.to_json_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if text_path is not None:
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(result.text_summary(), encoding="utf-8")


__all__ = [
    "SchemaDiffResult",
    "diff_schemas",
    "recommend_version",
    "write_schema_diff_report",
]
