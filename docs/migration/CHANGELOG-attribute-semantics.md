# Attribute semantics migration (ConceptualProperty / Domains)

## 2026-10-05 — PR-5 removal (strict typing) — schema **1.0.0** (major)

**Stability note:** `1.0.0` is the first declared-stable DAMS schema release for this
stack — TechnicalAsset hierarchy (ADR-031..033), semantic layer / ConceptualProperty
(ADR-034..035), and the DataType / ValueDomain type system (ADR-036..037). Prior
`0.1.0` was initial development; the jump `0.1 → 1.0.0` is both «first stable» and
a breaking change (removed deprecated LogicalAttribute slots).

Breaking for DAMS (path `0.1/` retained; schema `version` field → `1.0.0`):

- Removed LogicalAttribute slots: `logical_type`, `format_pattern`, `value_set_ref`,
  `unit_code`.
- Live schema no longer imports `moex-deprecated-slots`; archive kept at
  `docs/migration/archive/moex-deprecated-slots.yaml`.
- `format_pattern` / `unit_code` retained on `ValueDomain` (`moex-datatypes.yaml`).
- Strict rule: attributes require `data_type_ref` and/or `value_domain_ref`
  (`DAMS-SEM-ATTR-TYPE` / ATR-001.c2 / ATR-006).
- Semantic diff: clearing was-deprecated slots → `BREAKING` /
  `DAMS-DIFF-DEPRECATE-REMOVE` (message contains «was deprecated»).
- Migration `--apply` strips remaining deprecated keys; consumers write typed refs only.
- `LogicalDataTypeEnum` retained as seed catalogue for starter DataType (ADR-036).
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
