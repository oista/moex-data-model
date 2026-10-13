---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-050: Containment parent refs (equality check)

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-044](ADR-044-model-element-decomposition.md), [ADR-045](ADR-045-executable-constraint-matrix.md), audit Wave C3

## Context

Architect audit (2026-10-01) noted that inline-owned children often repeat a parent
ref (`LogicalAttribute.owner_entity_ref`, similar patterns for fields/bindings).
Options:

1. Derive the parent ref and forbid it in source YAML.
2. Keep the ref required but validators check equality with the container.
3. Promote children to top-level addressable nodes with references only.

Derive/forbid is the preferred long-term Git-authoring shape, but it is a
breaking data migration. Wave C needs an executable rule without a new schema major.

## Decision

### D1. Equality check now (non-breaking for valid data)

For `LogicalAttribute` inlined under `LogicalEntity.attributes[]`, if
`owner_entity_ref` is present it **must equal** the containing entity's
`element_id`. Violation is an **error** (`DAMS-INV-052` / INV-052), not a warning.

Former warning code `DAMS-STRUCT-005` remains a documented alias.

### D2. Derive/forbid deferred

Forbidding or deriving `owner_entity_ref` in authored YAML is deferred to a
breaking train under ADR Compatibility / Identity (audit Wave D). Until then
the slot stays required in schema for existing packages.

### D3. Scope

This ADR covers the LogicalAttribute / LogicalEntity containment pair called out
in the audit. Analogous equality checks for other parent-ref pairs may be added
as further INV rows without amending D1–D2.

## Consequences

- `moex_dams.rules.structural.check_structural_data` emits INV-052 as error.
- Constraint matrix row INV-052 with positive/negative fixtures.
- No schema major; no data rewrite for packages that already keep owner equality.
