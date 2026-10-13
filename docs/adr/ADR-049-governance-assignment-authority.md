---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-049: Governance assignment authority

**Date:** 2026-10-12  
**Status:** Accepted (PR-5 landed: legacy assignment target/id slots removed; schema **5.0.0**)  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-023](ADR-023-governed-property-cascade.md), [ADR-013](ADR-013-specification-requirements-catalog.md), [ADR-044](ADR-044-model-element-decomposition.md), [ADR-045](ADR-045-executable-constraint-matrix.md), [ADR-047](ADR-047-repository-manifest-and-lock.md), [ADR-048](ADR-048-topology-ownership.md)  
**Inventory:** [governance-inventory.md](../migration/governance-inventory.md)

## Context

Governance is expressed in two ways at once:

1. **Embedded (inline):** mixins `HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings` put `data_owner_ref` / `governance_classification` / `policy_refs` on model elements.
2. **Reified:** root collections `classification_assignments` / `policy_bindings` hold dated, approved objects (`ClassificationAssignment`, `PolicyBinding`) with validity and provenance.

[ADR-023](ADR-023-governed-property-cascade.md) already separates *declared* inline values from *effective* cascade values and forbids writing effective values back into YAML. Its resolver, however, reads **inline slots only**. Assignment objects are an unused extension point. That leaves two authored sources for the same fact (for example “table X is confidential”) with no priority rule, no inheritance via assignment scope, and no shared effective artifact for consumers.

Instance reality (see inventory): hundreds of inline governance values in packages; **zero** assignment instances in `implementations/` or examples. Generators (OWL/SHACL) emit schema shapes; runtime readers (`cascade.py`, `formal_checks.py`, `diff.py`) never merge assignments into effective values.

## Decision

### D1. Two authored modes; no third

| Mode | What | Role |
|---|---|---|
| Authored defaults | Inline mixin slots on elements | Lower layer; containment cascade per ADR-023 unchanged |
| Authoritative assignments | `GovernanceAssignment` and subtypes | Upper layer; overrides cascade for validity window and scope |
| Effective view | Generated `EffectiveGovernanceView` | Read model only; never hand-authored in DAMS |

There is **no** third mode: slots named `effective_*` (or equivalent) are not introduced on DAMS elements. Hand-writing an “effective” value is not expressible and must fail validation / checks.

### D2. Priority rules (as_of)

For a governed family and element `E` on check date `as_of`:

1. Consider assignments with `approval_status = approved`, `as_of` in `[valid_from, valid_to]` (open-ended if a bound is absent), whose target covers `E`: target = `E` (`assignment_scope = element`) or an ancestor of `E` when `assignment_scope = subtree`.
2. The **nearest target** wins (`E` more specific than an ancestor). This yields “classified on the schema, applies to all tables unless overridden”.
3. Two approved assignments of the same family on the **same** target with overlapping windows and different values: **error** `conflicting_assignments` (no silent winner).
4. If no assignment applies: use the ADR-023 inline cascade unchanged.
5. Policies: `PolicyBinding.binding_effect` is `replace` (default, list-replace like ADR-023) or `add` (union onto the next lower layer). `exclude` is not introduced.
6. Provenance: effective resolution returns `layer` (`assignment` | `inline` | `none`) and `assignment_id` when applicable.
7. An inline value shadowed by an active assignment: lint `shadowed_default` (**warning**), not an error.

### D3. Schema shape (additive, then cleanup)

- Abstract `GovernanceAssignment` (mixins `HasValidity`, `HasProvenance`): `assignment_id`, `target_element_ref`, `assignment_scope` (`element` | `subtree`), `approval_status`.
- Subtypes: existing `ClassificationAssignment`, `PolicyBinding`; new `OwnershipAssignment` (ownership family slots).
- Legacy target/id slots (`classified_element_ref`, `policy_target_ref`, `policy_binding_id`) receive a deprecation window (PR-1…PR-4), then removal (PR-5).
- Mixin descriptions state: authored default; overridden by assignment; effective value is not stored here.
- Root gains `ownership_assignments` beside existing assignment collections.

### D4. EffectiveGovernanceView module (not DAMS schema glob)

Mirror [ADR-048](ADR-048-topology-ownership.md) / ADR-047: `EffectiveGovernanceView` lives under `model-assets/specifications/moex-governance-view/0.1/`, is **not** imported by `moex-dams.yaml`, and is marked `materialized: true`. Output directory: `generated/governance/`. Integrity: `materialize --check` / step `check-governance` in `check_all`. CI uses a configured `as_of` (not wall-clock) so diffs do not drift.

### D5. Consumers

- `resolve_governed(body_data, *, as_of=None)` applies D2; with no assignments behaviour matches ADR-023.
- formal_checks with `effective: true` read the merged resolver.
- Semantic diff continues to compare **declared** inline slots and treats assignment objects as first-class objects (not materialized effective slots).
- Viewer may read `EffectiveGovernanceView` for display; deep UI is out of this ADR’s delivery scope.

### D6. Series PR

| PR | Theme |
|---|---|
| PR-0 | This ADR + inventory (docs; no schemas / `generated/`) |
| PR-1 | Additive DAMS schema + deprecated legacy target slots; regen |
| PR-2 | Resolver reads assignments + diagnostics + tests |
| PR-3 | `moex-governance-view` + materializer + `check-governance` |
| PR-4 | INV-042+ + fixtures + formal_checks / viewer / diff consumers |
| PR-5 | Remove deprecated slots (major), migration script, docs, regen |

Schema diff and data diff must not mix. `check_all` green on each PR separately. New invariants start at **INV-042** (INV-038…041 are topology).

### D7. Audit name map (Wave D4)

| Audit name | DAMS representation |
|---|---|
| `OwnershipAssignment` | `OwnershipAssignment` |
| `ClassificationAssignment` | `ClassificationAssignment` |
| `PolicyAssignment` | `PolicyBinding` (name retained; treat as policy assignment) |
| `StewardshipAssignment` | Folded into `OwnershipAssignment` (steward actor slots) — no separate class |

Executable invariants for this ADR are **INV-054…INV-056** on current `main` (original series used INV-042…044; renumbered on land to avoid Wave C collisions).

### D8. Wave D4 consumer hardening

- Preferred import: `moex_dams.rules.assignment_resolver` (`resolve_governed` / `diagnose_governance`).
- Multiple `PolicyBinding` with `binding_effect=replace` at the same nearest target and **different** `policy_ref` sets → `conflicting_assignments` (closes D2 gap).
- `formal_checks` accept `as_of` / `assignments` / `repo_root` (loads configured `as_of` from `moex-governance-view`).
- `EffectiveGovernanceView` discovery includes ADR-047 manifest package bodies (plus curated examples / `*.governance.yaml`).

### Out of scope

- `security_classification` / `sensitivity_term_refs` (Wave 2; same as ADR-023)
- `classification_term_ref` does not drive effective `governance_classification`
- Live external policy engines; Neo4j operational graph (ADR-003)
- Union of policies without `binding_effect`
- Physical move of `_apply_assignments` out of `cascade.py` (shared helpers; deferred to avoid import cycles)

## Consequences

- One authoritative story for “what is effective”: assignment when present and approved, else cascade.
- Existing packages keep inline defaults; no bulk data rewrite in PR-0…PR-4.
- External consumers of old target slot names get a major bump and a migration script in PR-5.
- ADR-023 remains the cascade norm; this ADR closes its assignment extension point.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Delete inline slots; assignments only | Breaks esed / xlsx import; loses package-level defaults |
| Write effective values into element slots | Recreates the dual SoT problem (this ADR’s subject) |
| Union of `policy_refs` without `binding_effect` | Ambiguous removal; rejected in ADR-023 |
| Put EffectiveGovernanceView inside `moex-dams` schemas | Violates ADR-047 boundary; forces DAMS regen on every materialize |
| Calendar-based deprecation | Zero assignment instances; PR-shaped window is enough |
