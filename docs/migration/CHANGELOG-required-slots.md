# Changelog: ADR-056 PR-8 catalog `slot_required` → LinkML `required`

**Aggregate version:** 5.4.0 (MINOR, class-level `slot_usage` only)  
**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md) PR-8, [ADR-051](../adr/ADR-051-dams-schema-compatibility.md)

## Why MINOR, not MAJOR

ADR-051 D2 lists “tighten requiredness” as MAJOR when the **global** slot `required` flag changes. This PR does **not** change `slots.title.required` or `slots.technology.required`. It sets **class `slot_usage`** on `LogicalEntity.title` and `DataCarrier.technology` so L1 LinkML matches catalog assess that already rejected missing values (PDM-001.c4 still error; LDM-002.c1 was superseded in PR-5 and is restored here at schema layer).

Authored solution packages (`ucd` / `mdm` / `esed` / `crm`) already populate both fields. The accepted instance set of production models is unchanged.

## Added (class `slot_usage`)

| Class | Slot | Catalog origin |
|---|---|---|
| `LogicalEntity` | `title` required | LDM-002.c1 (Group A → schema) |
| `DataCarrier` | `technology` required | PDM-001.c4 (Group C → schema before PR-9) |

`AccessPoint`, `DataContainer`, and `ExecutionAsset` keep `technology` optional (TechnicalAsset `slot_usage` `required: false`).

## Already in schema (no change)

| Catalog check | LinkML |
|---|---|
| GEN-001.c1–c4/c6 | `element_id`, `name`, `ModelPackage.description`, `lifecycle_status`, `api_version`, `model_version` |
| LDM-002.c2/c4 | `name`, `lifecycle_status` |
| ATR-001.c1/c3/c4 | `owner_entity_ref`, `required`, `multivalued` |
| REF-001.c1/c2 | `source_entity_ref`, `target_entity_ref` |
| PDM-001.c1–c3/c6/c7 | `system_ref`, `asset_kind`, `qualified_name`, `lifecycle_status`, `asset_namespace` |
| PDM-002.c1 | `SchemaNode.local_key` |

## Left in catalog (not schema-required)

| Check | Why |
|---|---|
| PDM-001.c5 `structure_ref` | Conditional (not for `in_memory`) |
| PDM-002.c2/c3 | Conditional on `node_kind=scalar` |
| GEN-001.c7 / LDM-11 | Cascade `data_owner_ref` |
| LDM-09 / LDM-10 | Cascade / mixed classification |
| LDM-001 `context_ref` / `solution_data_role` | Already schema-required (pre-PR-8). Relaxing is PR-10 if Group D drops the catalog row |

Catalog rows themselves are **not** removed in this PR (PR-9).

## Migration

None for authored YAML. L2 invariant fixtures that omitted `title` / `technology` are filled in a follow-up data commit so they remain complete packages.
