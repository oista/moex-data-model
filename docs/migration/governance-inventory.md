# Governance assignment authority inventory

**Date:** 2026-10-12  
**ADR:** [ADR-049](../adr/ADR-049-governance-assignment-authority.md)  
**Related cascade:** [ADR-023](../adr/ADR-023-governed-property-cascade.md)  
**Scope:** where governance facts live today (inline vs reified) before the Governance assignment authority series.

## Schema source

Primary governance module: [`moex-governance.yaml`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml)  
Root assignment collections: [`moex-dams.yaml`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml) (`classification_assignments`, `policy_bindings`)  
Merged schema copy: [`moex-dams-full.yaml`](../../model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml)  
Schema version at inventory: **4.0.0**

## Inline (authored default) slots

| Family | Slots | Mixins | Cascade (ADR-023) |
|---|---|---|---|
| ownership | `data_owner_ref`, `data_steward_ref`, `owning_unit_ref` | `HasOwnership` | yes (scalar) |
| classification | `governance_classification` | `HasGovernanceClassification` | yes (scalar) |
| policies | `policy_refs` | `HasPolicyBindings` | yes (list-replace) |

Not in cascade (unchanged by this series): `entity_type`, `data_class`, `business_importance`, `security_classification`, `sensitivity_term_refs`, `ownership_inheritance_rule` (rationale only).

## Reified assignment classes (today)

| Class | Identifier slot | Target slot | Collections on root |
|---|---|---|---|
| `ClassificationAssignment` | `assignment_id` (via base) | `target_element_ref` (via base; legacy `classified_element_ref` removed in 5.0.0) | `classification_assignments` |
| `PolicyBinding` | `assignment_id` (via base; legacy `policy_binding_id` removed in 5.0.0) | `target_element_ref` (via base) | `policy_bindings` |
| `OwnershipAssignment` | `assignment_id` | `target_element_ref` | `ownership_assignments` (added PR-1) |

Shared today: `HasValidity` on both classes; `approval_status`; classification also has `governance_classification`, `classification_source`, `classification_rationale`. No shared abstract base, no `assignment_scope` (self/subtree).

## Instance counts (2026-10-12)

Counts from YAML under `model-assets/implementations/**` and `model-assets/specifications/moex-dams/0.1/examples/**`:

| Pattern | Occurrences |
|---|---:|
| `governance_classification:` | 237 |
| `data_owner_ref:` | 33 |
| `policy_refs:` | 1 |
| `classification_assignments:` / `policy_bindings:` as instance keys | 0 in package bodies (schema-only in `moex-dams-full.yaml`) |

Conclusion: **inline is the lived authored surface**; assignment collections are unused. Choosing “inline = authored defaults” avoids a data rewrite for PR-0…PR-4.

## Code consumers

| Path | Role today |
|---|---|
| `packages/specification-dams/.../rules/cascade.py` | Effective values from **inline only**; provenance `(value, source_element_id, level)` |
| `packages/specification-dams/.../rules/formal_checks.py` | `effective: true` on GEN-001 / LDM-002 / LDM-003 via cascade |
| `packages/specification-dams/.../application/diff.py` | Compares declared `governance_classification` (and related) |
| `packages/specification-dams/tests/test_cascade_resolver.py` | Cascade regression |
| `apps/viewer/.../linkml_normalizer.py` | Prose that governance is mixins + PolicyBinding / ClassificationAssignment |
| OWL / SHACL / JSON Schema generators | Emit class/slot shapes; do not resolve effective instance values |

## Implications for migration

- No bulk rewrite of esed / import packages for defaults.
- Deprecation window is PR-shaped (PR-1…PR-4) for legacy target/id slot names on assignment classes.
- PR-5 migration script primarily targets external consumers of `classified_element_ref` / `policy_target_ref` / `policy_binding_id`.
- New invariants start at INV-042 (INV-038…041 reserved for topology ownership).
- Effective read model must live outside `moex-dams/0.1/schemas/` (ADR-047 / ADR-048 pattern).
