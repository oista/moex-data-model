# Golden / artifacts diff notes — Domains & ConceptualProperty / PR-5

Date: 2026-10-05  
Trigger: schema modules `moex-semantic`, `moex-datatypes`; PR-5 removal of
deprecated LogicalAttribute slots; schema `version` → **1.0.0**.

## PR-5 regenerations (manual review)

| Artifact | Observation |
|---|---|
| python / contracts | `LogicalAttribute` no longer has `logical_type` / `format_pattern` / `value_set_ref` / `unit_code`; `data_type_ref` optional on LA, required on ValueDomain / NativeTypeBinding |
| owl / shacl / json-schema | Slot removals + version bump; ValueDomain retains format/unit |
| dbml / mermaid | No LogicalAttribute columns for removed slots |
| ontology-report / doc | Inventory without removed LA slots |
| release bundle | Rebuilt after contracts+artifacts; digests updated in manifests |

## Regenerated digests (earlier Domains work)

| Artifact | Notes |
|---|---|
| contracts | New Pydantic types for DataType, ValueDomain, ConceptualProperty, … |
| owl / rdf | New classes; LinkML gen maps `exact_mappings`/`close_mappings` where set |
| shacl | Shape growth for new classes/slots |
| dbml / mermaid / json-schema / python / doc | Include new classes; inlined ValueMeaning/PermissibleValue need identifier slots |
| ontology-report | Updated class inventory |

## Fixes required for generators

1. **Conflicting URIs `native_type`**: `NativeTypeBinding` renamed slot → `dialect_native_type` (ADR-036).
2. **DBML identifier**: `meaning_key`, `value_code`, `value_set_query_id` marked `identifier: true`.
3. LinkML rules with `equals_string` on enums emit “ignoring equals_string=… as unable to tell if literal” — noise only; semantic rules enforced in DAMS-валидаторе.

## Expected golden churn (PR-5)

Breaking churn: removal of deprecated LA slots from generated surfaces; major schema
version field `1.0.0` (asset path `moex-dams/0.1/` unchanged). Archive of
`moex-deprecated-slots` lives under `docs/migration/archive/` and is not imported.
