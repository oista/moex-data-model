# Attribute semantics migration (ConceptualProperty / Domains)

- Schemas: `moex-semantic.yaml`, `moex-datatypes.yaml`, `moex-deprecated-slots.yaml`
- Classes: ConceptualProperty, ConceptualDomain, ValueMeaning, DataType, NativeTypeBinding, ValueDomain, PermissibleValue
- LogicalAttribute: optional `concept_ref`, `value_domain_ref`, `data_type_ref`, `critical_data_element`
- Deprecated (step 2 file): `logical_type`, `format_pattern`, `value_set_ref`, `unit_code`
- Migration: `scripts/migrate_logical_attribute_semantics.py` (`--apply` types/domains only; `--propose` properties)
- Coverage: `moex-model concept-coverage`
- ADRs: 034–037
