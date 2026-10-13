# Changelog: audit Wave C (schema 4.1.0)

Non-major hardening after ADR-048 (4.0.0). No authored data migration required.

## 4.1.0

**Schema**

- `RealizesMapping.source_refs`: `any_of` LogicalEntity | ConceptualEntity (aligned with L2 INV-035).
- Deprecated orphan slots `native_name` / `native_type` on `moex-core` (no class usage).
- Deprecated `transformation_ref` / `transformation_expression` on `Mapping` (no Transformation type).
- `LogicalDataTypeEnum` marked deprecated (ADR-036 seed only).

**Constraints**

- INV-042..053 implemented (L2 fixtures under `examples/invariants/l2/`).
- ADR-050: containment parent-ref equality (`owner_entity_ref`) as error INV-052.

**Tooling**

- `tools/architecture-check`: redundant mixin lint; description allowlist must match ADR-044 section.
