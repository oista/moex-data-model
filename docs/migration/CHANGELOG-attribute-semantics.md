# Attribute semantics migration (ConceptualProperty / Domains)

## 2026-10-05 — PR-5 removal (strict typing)

Breaking for DAMS 0.1 draft (in-repo only):

- Removed LogicalAttribute slots: `logical_type`, `format_pattern`, `value_set_ref`,
  `unit_code`.
- Deleted schema module `moex-deprecated-slots.yaml` (imports dropped from
  `moex-core` / `moex-dams`).
- `format_pattern` / `unit_code` retained on `ValueDomain` (`moex-datatypes.yaml`).
- Strict rule: attributes require `data_type_ref` and/or `value_domain_ref`
  (`DAMS-SEM-ATTR-TYPE` / ATR-001.c2 / ATR-006).
- Migration `--apply` strips remaining deprecated keys; consumers write typed refs only.
- Residue: `tests/architecture/test_attribute_semantics_residue.py`

## 2026-10-05 — Deprecation release (pre–PR-5)

Shipped as an in-repo **deprecation release**: deprecated LogicalAttribute slots remain
in the schema with LinkML metadata; consumers and models must prefer typed refs.
External consumers are not assumed — changelog + ADR gate the window before removal.

### Schemas
- `moex-semantic.yaml`, `moex-datatypes.yaml` (deprecated slots module removed in PR-5)
- Classes: ConceptualProperty, ConceptualDomain, ValueMeaning, DataType,
  NativeTypeBinding, ValueDomain, PermissibleValue
- LogicalAttribute: optional `concept_ref`, `value_domain_ref`, `data_type_ref`,
  `critical_data_element`

### Migration / policy
- Script: `scripts/migrate_logical_attribute_semantics.py`
  (`--apply` types/domains only; `--propose` properties; `--demo` for digest)
- Denylist: `moex-dams-full.yaml`
- Binding integrity: `moex_dams.application.binding_revision`
- Coverage: `moex-model concept-coverage`
- ADRs: 034–037 (accepted); ADR-031 integrity_digest clause closed

### Acceptance
- Residue (typed refs; banned keys gone):
  `tests/architecture/test_attribute_semantics_residue.py`
- Slot removal: `packages/specification-dams/tests/test_deprecated_slots_metadata.py`
- Binding revision: `packages/specification-dams/tests/test_binding_revision.py`
