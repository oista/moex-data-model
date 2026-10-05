# Attribute semantics migration (ConceptualProperty / Domains)

## 2026-10-05 — Deprecation release (pre–PR-5)

Shipped as an in-repo **deprecation release**: deprecated LogicalAttribute slots remain
in the schema with LinkML metadata; consumers and models must prefer typed refs.
External consumers are not assumed — changelog + ADR gate the window before removal.

### Schemas
- `moex-semantic.yaml`, `moex-datatypes.yaml`, `moex-deprecated-slots.yaml`
- Classes: ConceptualProperty, ConceptualDomain, ValueMeaning, DataType,
  NativeTypeBinding, ValueDomain, PermissibleValue
- LogicalAttribute: optional `concept_ref`, `value_domain_ref`, `data_type_ref`,
  `critical_data_element`
- Deprecated (step 1, still present): `logical_type`, `format_pattern`,
  `value_set_ref`, `unit_code` — each with `deprecated` +
  `deprecated_element_has_possible_replacement`

### Migration / policy
- Script: `scripts/migrate_logical_attribute_semantics.py`
  (`--apply` types/domains only; `--propose` properties; `--demo` for digest)
- Denylist: `moex-dams-full.yaml`
- Binding integrity: `moex_dams.application.binding_revision`
  (demo recompute vs production new revision + `compatibility_baseline_ref`)
- Coverage: `moex-model concept-coverage`
- ADRs: 034–037 (accepted); ADR-031 integrity_digest clause closed

### Acceptance
- Residue (typed refs on solution attrs):
  `tests/architecture/test_attribute_semantics_residue.py`
- Deprecated slot metadata: `packages/specification-dams/tests/test_deprecated_slots_metadata.py`
- Binding revision: `packages/specification-dams/tests/test_binding_revision.py`

### Next (requires explicit «да»): PR-5
- Move deprecated slots fully into `moex-deprecated-slots.yaml` then remove
- Enable strict typing rule (no sole `logical_type`)
