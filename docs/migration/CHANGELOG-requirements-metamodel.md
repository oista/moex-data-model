# Changelog: ADR-056 requirements catalog metamodel (aggregate 5.2.0)

Additive minor (ADR-051 D2): catalog shape only; **no** instance catalog rewrite in this PR.

## Schema

- `SpecificationRequirement.code` pattern `^(CDM|LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{2,3}$` (two-digit backbone codes + historical three-digit).
- `RequirementSectionEnum` gains `CDM`.
- Optional slots `obligation` (`mandatory` | `recommended`) and `responsible_role` (`data_architecture` | `it_owner` | `business_owner`).
- `formal_checks` `minimum_cardinality` 1 → 0 (manual rules / human-review per ADR-013).
- Aggregate `moex-dams.yaml` version **5.1.0 → 5.2.0**.

## Semantic gate

- `catalog_validate.CODE_PATTERN` matches the schema pattern.
- Empty `formal_checks` no longer emits `CATALOG-CHECKS-MISSING`.

## Out of this PR

- Backbone rows CDM-01…PDM-02 (PR-4).
- Runner lifecycle skip (PR-2).
- Existing IT-solution / conceptual catalog instances unchanged.

## PR-2: runner honours requirement lifecycle (no schema change)

- `check_formal_requirements` skips requirements with `lifecycle_status` `deprecated`, `superseded` or `rejected`; `draft`, `proposed` and `approved` stay enforced.
- `load_it_solution_catalog` still returns every row (viewer / export keep showing deprecated requirements).
- No behaviour change on the current catalog: all rows are `approved`. Prerequisite for PR-5 (mass `superseded` without double-firing).
