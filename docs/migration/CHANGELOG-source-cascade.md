# CHANGELOG: source / data_class cascade (ADR-056 PR-7b)

**Aggregate version:** 5.3.0 (MINOR, additive)  
**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md), amends [ADR-023](../adr/ADR-023-governed-property-cascade.md)

## Added

| Surface | Change |
|---|---|
| Mixin `HasDataSource` | Optional `source_system_refs` → `ITSystem` (multivalued, list-replace cascade) |
| `LogicalEntity` | Mixin `HasDataSource` |
| `LogicalAttribute` | Mixin `HasDataSource`; optional `data_class` (override of entity) |
| Slot `data_class` description | Documents entity vs attribute cascade (LDM-09) |

## Not changed

- `ModelPackage` does not declare `data_class` or `source_system_refs`.
- Assignment layer / `GOVERNED_SLOTS` / `EffectiveGovernanceView` unchanged in this PR (cascade code lands in PR-7c).
- Existing instances remain valid (new slots optional).

## Migration

None required for authored YAML. Optional fill of `source_system_refs` is PR-7f.
