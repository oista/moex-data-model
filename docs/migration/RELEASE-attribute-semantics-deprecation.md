# Release: Attribute semantics deprecation window

**Date:** 2026-10-05  
**Scope:** in-repository models and DAMS 0.1 draft only  
**Status:** deprecation release (slots still present; removal = PR-5)

## What this release ships

1. Corporate typing via `DataType` / `ValueDomain` / optional `ConceptualProperty`
   (variant B: attributes without conceptual pair remain valid).
2. Deprecated LogicalAttribute slots retained with LinkML deprecation metadata and
   documented replacements (`data_type_ref` / `value_domain_ref`).
3. Closed binding revision policy (`integrity_digest`): demo recomputes in place;
   production issues a new `model_revision` with `compatibility_baseline_ref`.
4. Architecture residue test: solution attributes must not rely on `logical_type`
   alone.

## Compatibility promise (deprecation window)

| Artifact | Promise until PR-5 |
|---|---|
| Schema slots `logical_type`, `format_pattern`, `value_set_ref`, `unit_code` | Present, marked deprecated |
| Solution ModelPackage YAML | Must expose `data_type_ref` and/or `value_domain_ref` |
| DataModelBinding digests | Immutable per revision; migrations bump revision |
| ConceptualProperty | Propose-only via migration; never auto-created |

## Out of scope

- PR-5 removal of deprecated slots (needs explicit go-ahead).
- SemVer bump of published packages beyond in-repo 0.1 draft (no external
  consumers assumed for this compressed release).

## References

- [CHANGELOG-attribute-semantics.md](CHANGELOG-attribute-semantics.md)
- [ADR-037](../adr/ADR-037-attribute-semantics-migration.md)
- [ADR-031](../adr/ADR-031-technical-asset-registry.md) (integrity_digest)
