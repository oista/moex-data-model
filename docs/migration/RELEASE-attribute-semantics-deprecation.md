# Release: Attribute semantics — PR-5 slot removal

**Date:** 2026-10-05  
**Scope:** in-repository models and DAMS 0.1 draft only  
**Status:** complete (deprecated LogicalAttribute slots removed)

## What changed vs deprecation window

| Artifact | After PR-5 |
|---|---|
| Schema slots `logical_type`, `format_pattern`, `value_set_ref`, `unit_code` on LogicalAttribute | **Removed** |
| `moex-deprecated-slots.yaml` | **Deleted** |
| Solution ModelPackage YAML | Must expose `data_type_ref` and/or `value_domain_ref` only |
| ValueDomain `format_pattern` / `unit_code` | Unchanged |
| DataModelBinding digests | Unchanged policy (ADR-031) |
| ConceptualProperty | Propose-only; never auto-created |

## Compatibility

This is a **breaking** schema change for any payload still carrying the removed
attribute keys. In-repo models and fixtures were stripped; migration `--apply`
continues to accept legacy keys as input and strips them on write.

## References

- [CHANGELOG-attribute-semantics.md](CHANGELOG-attribute-semantics.md)
- [ADR-034](../adr/ADR-034-lightweight-conceptual-property.md)
- [ADR-037](../adr/ADR-037-attribute-semantics-migration.md)
