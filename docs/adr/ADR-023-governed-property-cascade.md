---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-023: Containment cascade of governed properties

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-001](ADR-001-linkml-yaml-canonical.md), [ADR-007](ADR-007-pydantic-dto-not-validator.md), [ADR-013](ADR-013-specification-requirements-catalog.md)  
**Requirements:** [IT_SOLUTION_MODEL_REQUIREMENTS.md](../architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md)

## Context

Governance mixins (`HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings`)
expose optional slots on model elements, but LinkML mixins do **not** define
instance-value inheritance. Today “inheritance” is either:

- a free-text `ownership_inheritance_rule` that formal_checks treat as sufficient,
  or
- copy-down of defaults onto every entity/attribute at xlsx import time.

Neither preserves the distinction between *declared override* and *inherited
effective value*. Classification and policies already appear on attributes
(§7.1 of the IT-solution requirements), but without a shared cascade they are
either stamped everywhere or left undefined.

`ClassificationAssignment` and `PolicyBinding` are a different axis: dated,
approved assignments — not the default containment cascade.

## Decision

Introduce a **containment cascade of governed properties**:

- YAML stores only **declared** values (absent key = inherit).
- A resolver computes **effective** values along the containment tree and
  returns provenance `(value, source_element_id, level)`.
- Catalog formal_checks may read `effective: true` instead of the raw element.
- Semantic diff continues to compare **declared** slots (overrides), not
  materialised copy-down.

This is **not** a LinkML mixin feature, not YAML materialisation, and not
text-rule inheritance.

### Cascade chains (v1)

`DomainContext` is **out** of the chain (independent ownership/context).

| Scope | Chain |
|---|---|
| Solution logical | `ModelPackage` → `LogicalEntity` → `LogicalAttribute` |
| Enterprise conceptual | `ModelPackage` → `ConceptualEntity` |
| Physical | `ModelPackage` → `PhysicalObject` → `PhysicalField` |

### Rules

1. Slot **absent** → effective value of parent.
2. Slot **present** → override at this level; descendants inherit that value.
3. Override is **per-slot** (an attribute may override only steward or only
   classification).
4. Lists (`policy_refs`): key absent = inherit; present list (including `[]`) =
   **full replace**, not union.
5. Effective values are **never** written back into the model YAML.

### Families (v1)

| Family | Slots | Cardinality | Root obligation |
|---|---|---|---|
| ownership | `data_owner_ref`, `data_steward_ref`, `owning_unit_ref` | scalar | package must declare `data_owner_ref` |
| classification | `governance_classification` | scalar | logical entity must have effective classification |
| policies | `policy_refs` | list-replace | none (optional) |

**Not in cascade:** `entity_type`, `data_class`, `business_importance`
(intrinsic entity axes); `security_classification` / `sensitivity_term_refs`
(Wave 2). Inheritance of **definitions** via the semantic chain
(`realizes` / `conceptual_entity_refs` / external exact sources) is specified
separately in [ADR-025](ADR-025-definition-cascade-and-glossary.md) — not as a
governed-family extension of this containment cascade.

### Relation to assignment classes

| Mechanism | Role |
|---|---|
| Inline cascade slots | Declared default on the element |
| `ClassificationAssignment` / `PolicyBinding` (+ future `OwnershipAssignment`) | Dated / approved exceptions |

v1 resolver reads **inline slots only**. Extension point: assignments override
cascade for their validity window.

### Functional surface

- Registry of families: name, slots, cardinality, root class, containment edges.
- API: `resolve_governed(body_data)` → per-element effective map with provenance.
- formal_checks flag `effective: true` on `slot_required` / `at_least_one_slots`.
- Info lint: declared value equal to parent effective → redundant override.
- Warning: effective `data_owner_ref` is a placeholder (`DATA_OWNER_PENDING`),
  reported once at the owning source element.
- `ownership_inheritance_rule` remains as human rationale only; it is **not**
  a substitute for `data_owner_ref`.

## Consequences

- Schema: every cascade node carries the relevant mixins
  (`LogicalAttribute` / `PhysicalField` gain ownership + classification +
  policies; `ModelPackage` gains classification + policies).
- Xlsx enrich must not stamp ownership/classification onto descendants.
- GEN-001 requires package `data_owner_ref`; LDM-002 / LDM-003 may pass via
  effective inheritance.
- Viewer may later show provenance; UI is out of this ADR’s delivery scope.

## Alternatives

| Alternative | Why not |
|---|---|
| Copy-down into YAML | Loses inherit vs override; breaks package-level updates; inflates semantic diff |
| XOR `data_owner_ref` / `ownership_inheritance_rule` | Text rule is not executable; already rejected as XOR in requirements |
| Union of `policy_refs` | Ambiguous removal; empty list cannot mean “no policies” |
| Inherit via `realizes` | Wrong axis for ownership/classification/policies; definitions use ADR-025 |
| Separate inheritance DSL | Overkill; containment tree already defines the chain |

## Related

- ADR-001 (YAML canonical), ADR-007 (DTO ≠ validator), ADR-013 (requirements catalog / formal_checks)
- ADR-025 (definition cascade on the semantic axis; closes the deferred realizes note for definitions only)
- ADR-026 (`entity_tier` / `genesis_kind` are structural metadata on ConceptualEntity; they do **not** participate in this containment cascade)
)
