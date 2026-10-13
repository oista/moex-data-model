---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-053: Qualified assertion pattern

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-023](ADR-023-governed-property-cascade.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-026](ADR-026-cmd-entity-metamodel.md), [ADR-044](ADR-044-model-element-decomposition.md), [ADR-046](ADR-046-typed-mapping-endpoints.md), ADR-049 governance assignment authority *(number reserved; not on main yet)*  
**Audit:** Wave D3 (Qualified relation / assertion decision gate)

## Context

The audit asked for a PROV-O-style qualified relation (Assertion / QualifiedRelation) shared by ownership, classification, mappings, alignments, and definitions. Today:

| Shape | Validity | Provenance | Confidence | Evidence |
|---|---|---|---|---|
| `Mapping` (+ subclasses) | via `HasLifecycle` → `HasValidity` | `HasProvenance` | own `confidence` slot | via `HasProvenance.evidence_refs` |
| `ExternalClassRef` | — | `HasProvenance` | — | `evidence_refs` |
| `ScopedDefinition` | — | `HasProvenance` | — | `evidence_refs` |
| Governance assignments (ADR-049) | `HasValidity` | `HasProvenance` | — | `evidence_refs` |

Two parallel alignment paths exist: **`ExternalClassRef`** (canonical on `ConceptualEntity`) and **`AlignsWithMapping`** (package collection, URI targets). Mapping still carries deprecated `transformation_ref` / `transformation_expression` without a Transformation type (Wave C deprecation).

## Decision

### D1. Mixin `HasAssertionMetadata` (additive, non-breaking)

Introduce in `moex-base.yaml` (or `moex-governance.yaml` if provenance stays there) a thin mixin:

```yaml
HasAssertionMetadata:
  mixin: true
  mixins: [HasValidity, HasProvenance]
  slots: [confidence]
```

- **`confidence`**: move definition to the shared slot home (range unchanged); `Mapping` keeps the slot via the mixin instead of a local list entry where possible.
- Apply to: `Mapping`, `ExternalClassRef`, `ScopedDefinition`, and (when ADR-049 lands) `GovernanceAssignment`.
- Do **not** introduce an abstract class `Assertion` / `QualifiedRelation` in the `is_a` backbone (ADR-044: keep backbone shallow; aspects are mixins).

Implementation: separate additive PR (minor bump), **not** this docs PR. Until then, the table in Context is the normative “as-is / to-be” contract.

### D2. Alignment paths: keep both, clarify roles

| Path | Role | Rules |
|---|---|---|
| `ExternalClassRef` | **Canonical** authored alignment on a conceptual element (match_kind, specification pin, selection) | Prefer for ontology / glossary / SKOS-style matches |
| `AlignsWithMapping` | **Package-level** projection / import mirror (URI targets, typed collection) | May mirror an ExternalClassRef; must not contradict it when both present (future L2 INV when both appear for the same concept+IRI) |

Rename to `SemanticAlignment` is **deferred** (breaking + consumer churn); track under P2 backlog. Docs and glossary map audit name → `ExternalClassRef`.

### D3. Transformation / design lineage

- **No** `Transformation` mapping subclass in the near term (no live `mapping_type: transformation` instances after ADR-046).
- Deprecated hooks `transformation_ref` / `transformation_expression` on `Mapping` are removed in the **6.0.0 identity train** (ADR-052 D5) unless a design-lineage ADR supersedes this decision first.
- Runtime lineage stays outside DAMS (OpenLineage platform). Optional future: `lineage_source_ref` on `ExecutionAsset` / design facet — P2, not Wave D.
- DAMS may store **design-time** derivation only after an explicit lineage ADR; until then do not reintroduce a polymorphic transformation mapping type.

### D4. Evidence and approval

`HasProvenance` remains the home for `source_artifact_ref`, `evidence_refs`, `approval_status`, `approved_by_ref`, `approved_at`. Assertion mixin composes it; do not duplicate those slots on subclasses.

### D5. Governance name map (audit ↔ schema)

When ADR-049 lands, document in that ADR (and repeat here for discoverability):

| Audit name | DAMS class / representation |
|---|---|
| `OwnershipAssignment` | `OwnershipAssignment` |
| `ClassificationAssignment` | `ClassificationAssignment` |
| `PolicyAssignment` | `PolicyBinding` (name retained; treat as policy assignment) |
| `StewardshipAssignment` | Folded into `OwnershipAssignment` (steward role / actor slots) — no separate class unless a later ADR splits it |

## Consequences

- Shared assertion vocabulary without deepening `is_a`.
- Alignment dual-path is intentional, not accidental dual truth — with a future consistency INV.
- Transformation hooks have an end date (6.0.0) unless lineage work reclaims them.

## Alternatives

| Alternative | Why not |
|---|---|
| Abstract `QualifiedRelation` in `is_a` | Collides with Mapping/IdentifiedElement; LinkML single backbone preference |
| Delete `AlignsWithMapping` now | Breaks typed collections / ADR-046 data |
| Build Transformation class now | No instances; YAGNI |

## Acceptance

- [x] Mixin design recorded
- [x] Alignment dual-path roles fixed
- [x] Transformation removal scheduled with identity train
- [ ] Schema mixin PR (minor; follow-up)
- [ ] Consistency INV ExternalClassRef ↔ AlignsWithMapping (follow-up)
