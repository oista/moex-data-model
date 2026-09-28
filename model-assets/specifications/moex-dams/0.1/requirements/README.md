# DAMS requirements catalogs

Machine-readable normative requirements for DAMS model packages
([ADR-013](../../../../docs/adr/ADR-013-specification-requirements-catalog.md)).

| Catalog | Path | Level |
|---------|------|-------|
| IT-solution | [`it-solution-requirements.yaml`](it-solution-requirements.yaml) | `it_solution` |
| Conceptual | [`conceptual-model-requirements.yaml`](conceptual-model-requirements.yaml) | `conceptual_model` |

## Fields

- **`statement`** — полная норма на русском для человека (без имён LinkML-классов/слотов).
- **`title`** — короткий технический ярлык.
- **`formal_checks`** — исполняемое подмножество (`slot_required`, `at_least_one_slots`,
  `conditional_branch`, …) с `diagnostic_code`, `severity`, `remediation`.
- **`applies_to`** — target class / kinds / implementation scope.

Absence of `formal_checks` means human-review, not silent pass.

## Gate composition

1. Schema / LinkML validation (including catalog self-validation)
2. Body assess — three buckets:
   - `assessment:standard-syntax`
   - `assessment:corporate-semantics` (structural / refs / ids / levels)
   - `assessment:model-requirements` (IT-solution `formal_checks` only)
3. Publication contract (ADR-019 — section presence / `satisfies` / semantic types)

**ADR-019 ≠ body assess.** Missing `identity_rule`, `ownership`, or
`mapping_coverage_status` on a model body does **not** fail the publication
contract; those fields are enforced only by `formal_checks`.

Viewer section `kind: model-assessment` (recommended on implementation
profile) projects `model_assessment` rows from `assessment:model-requirements`.

## Mapping aliases (ADR-019)

Publication profiles may list semantic types `EntityPhysicalMapping` /
`AttributePhysicalMapping` as **viewer aliases**. Canonical LinkML class is
`Mapping` with `mapping_type`: `entity_physical` | `field_mapping` | …

## Wave 2 follow-ups

- Reject or warn `business_key_kind: surrogate` without `key_attribute_refs`
  even when `identity_rule` is present (Wave 1 allows this combination).
- Framework-only check kinds `slot_min_cardinality` / `key_subset` remain in
  `FormalCheckKindEnum` but unused by the catalog until needed.

## Severity

See severity matrix in [ADR-013](../../../../docs/adr/ADR-013-specification-requirements-catalog.md).
Wave 1 = model exists and is traceable; Wave 2 = modeling quality (warnings).
