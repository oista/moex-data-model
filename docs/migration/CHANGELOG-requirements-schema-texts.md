# Changelog: ADR-056 PR-10e schema texts and `security_classification`

**Aggregate version:** 5.5.0 (MINOR, deprecate without removal)  
**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md) PR-10e, [ADR-051](../adr/ADR-051-dams-schema-compatibility.md)

## Why MINOR, not MAJOR

ADR-051 D2 treats “deprecate without removal” as MINOR. This PR does not delete slots, change `required`, or alter ranges. `security_classification` stays on instances until a later MAJOR series removes it.

## Changed

| Surface | Change |
|---|---|
| `security_classification` | `deprecated: true`; description points at `governance_classification` |
| `isolation_rationale` | Drop retired catalog code LDM-007 from the slot description |
| `EntityPhysicalMapping` / `MappingTypeEnum.entity_physical` | Cite backbone PDM-02 instead of retired PDM-003 |
| `Applicability.applicability_id` | Example `appl:LDM-01` (backbone), not `appl:LDM-001` |

## Not changed

- Authored YAML may still set `security_classification`.
- Catalog rows for Group D were deleted in PR-10f (after this schema PR).
- No data migration.

## Migration

None for authored YAML. Stop filling `security_classification` on new entities; use `governance_classification`.
