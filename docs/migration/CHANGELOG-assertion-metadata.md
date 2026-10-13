# Changelog: ADR-053 HasAssertionMetadata (aggregate 5.1.0)

Additive minor (ADR-051 D2): new mixin + L2 invariant; no data migration required.

## Schema

- New mixin `HasAssertionMetadata` in `moex-governance.yaml`: `HasValidity` + `HasProvenance` + `confidence`.
- Applied to `Mapping`, `ExternalClassRef`, `ScopedDefinition`, `GovernanceAssignment` (replacing direct `HasProvenance` / `HasValidity`+`HasProvenance` listings).
- Slot `confidence` definition moved from `moex-core.yaml` to `moex-governance.yaml` (shared home).
- Aggregate `moex-dams.yaml` version **5.0.0 → 5.1.0**.

## Constraints

- **INV-057**: when the same concept + external IRI appears on both `ExternalClassRef` and `AlignsWithMapping`, confidence and approval_status must not contradict.

## Docs

- ADR-053 Acceptance checkboxes closed.
- P2-BACKLOG F0-1 / F0-2 marked done.
