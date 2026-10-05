# Golden / artifacts diff notes — Domains & ConceptualProperty

Date: 2026-10-05  
Trigger: schema modules `moex-semantic`, `moex-datatypes`, `moex-deprecated-slots`;
narrowed `LogicalAttribute`; `ConceptualProperty`.

## Regenerated digests (after SchemaLoader fixes)

| Artifact | Notes |
|---|---|
| contracts | New Pydantic types for DataType, ValueDomain, ConceptualProperty, … |
| owl / rdf | New classes; LinkML gen maps `exact_mappings`/`close_mappings` where set |
| shacl | Shape growth for new classes/slots |
| dbml / mermaid / json-schema / python / doc | Include new classes; inlined ValueMeaning/PermissibleValue need identifier slots |
| ontology-report | Updated class inventory |
| release bundle | `scripts/build_release_bundle.py` after contracts+artifacts |

## Fixes required for generators

1. **Conflicting URIs `native_type`**: `NativeTypeBinding` renamed slot → `dialect_native_type` (ADR-036).
2. **DBML identifier**: `meaning_key`, `value_code`, `value_set_query_id` marked `identifier: true`.
3. LinkML rules with `equals_string` on enums emit “ignoring equals_string=… as unable to tell if literal” — noise only; semantic rules enforced in DAMS-валидаторе.

## Expected golden churn

Large additive churn (new classes/slots), not a silent rewrite of existing LogicalAttribute
required fields beyond `logical_type` becoming optional/deprecated.
