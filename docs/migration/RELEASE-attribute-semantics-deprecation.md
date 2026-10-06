# Release: Attribute semantics — PR-5 slot removal

**Date:** 2026-10-05  
**Schema version:** **1.0.0** (major; asset path `moex-dams/0.1/` unchanged)  
**Scope:** in-repository models and DAMS  
**Status:** complete (deprecated LogicalAttribute slots removed)

**Stability:** `1.0.0` declares stable this stack — TechnicalAsset hierarchy,
semantic layer / ConceptualProperty, and DataType / ValueDomain. Prior `0.1`
was initial development; `0.1 → 1.0.0` is first-stable **and** breaking.

## What changed vs deprecation window

| Artifact | After PR-5 |
|---|---|
| Schema slots `logical_type`, `format_pattern`, `value_set_ref`, `unit_code` on LogicalAttribute | **Removed** |
| Live `moex-deprecated-slots.yaml` | **Not imported**; archive at `docs/migration/archive/moex-deprecated-slots.yaml` |
| Solution ModelPackage YAML | Must expose `data_type_ref` and/or `value_domain_ref` only |
| ValueDomain `format_pattern` / `unit_code` | Unchanged |
| Semantic diff clearing was-deprecated keys | **BREAKING** (`DAMS-DIFF-DEPRECATE-REMOVE`, message contains «was deprecated») |
| DataModelBinding digests | Non-demo: new revision + `compatibility_baseline_ref` (ADR-031); demo may recompute |
| ConceptualProperty | Propose-only; never auto-created |
| `LogicalDataTypeEnum` | Kept as starter DataType name catalogue (ADR-036) |

## Compatibility

Breaking schema change for payloads still carrying removed attribute keys.
In-repo models stripped; migration `--apply` accepts legacy keys as input and strips them on write. Consumers no longer fall back to removed slots.

## References

- [CHANGELOG-attribute-semantics.md](CHANGELOG-attribute-semantics.md)
- [golden-diff-attribute-semantics.md](golden-diff-attribute-semantics.md)
- [ADR-034](../adr/ADR-034-lightweight-conceptual-property.md)
- [ADR-036](../adr/ADR-036-datatype-system.md)
- [ADR-037](../adr/ADR-037-attribute-semantics-migration.md)
