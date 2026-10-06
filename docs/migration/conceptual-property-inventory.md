# ConceptualProperty migration: LogicalAttribute slot inventory

Инвентаризация слотов `LogicalAttribute` / связанных полей сущностей для миграции на `ConceptualProperty` (корпоративный уровень) и переноса domain-семантики с solution-bound атрибутов.

**Target class (planned):** `ConceptualProperty` — в схемах и данных **отсутствует** (grep 0 hits вне служебных скриптов инвентаризации).

**Patterns:** см. таблицу слотов в Summary; плюс mixin-ссылки на `LogicalAttribute`.

**Excluded:** `generated/**`, `tmp/**`, `node_modules/**`, `.git/**`, `.cursor/plans/**`.

**Source:** live `rg` via `docs/migration/_build_conceptual_property_inventory.py`. Raw line hits: 2073; unique files: 108.

---

## Summary: key slots / classes

| Concept | Location | Notes |
|---|---|---|
| `LogicalAttribute` property slots | `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml:124-154`, slot defs `:437-493` | `logical_type`, `value_set_ref`, `format_pattern`, `default_value`, `derived_expression`, Wave-2: `unit_code`, `currency_attribute_ref`, `timezone_policy`, `temporal_semantics` |
| `LogicalAttribute` mixins | `moex-core.yaml:126-130` | `HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings`, `HasDefinition` (**not** `HasBusinessClassification`) |
| `LogicalEntity` identity / alignment | `moex-core.yaml:110-116`, slot defs `:460-473` | `key_attribute_refs`, `identity_rule`, `business_key_kind`, `conceptual_alignment_status`, `alignment_rationale`, `isolation_rationale` |
| `ConceptualEntity` CMD slots | `moex-core.yaml:81-87`, slot defs `:370-402` | `key_attribute_refs` (shared slot, range `uriorcurie`), `genesis_kind`, `external_class_refs` |
| `HasDefinition` | `moex-governance.yaml:105-111`, slot defs `:209-219` | `definition_source_ref`, `definition_rationale`, `scoped_definitions` |
| `HasBusinessClassification` | `moex-governance.yaml:60-66`, `:178` | `entity_type`, `data_class`, `business_importance` (entity-level; не на LogicalAttribute) |
| `LogicalDataTypeEnum` | `moex-types.yaml:243+` | Range of `logical_type`; `identifier` описан как tech key, не замена `identity_rule` |

### Counts by inventory category

| Category | Files | Line hits |
|---|---:|---:|
| 1. Schemas | 5 | 70 |
| 2. Requirements | 4 | 39 |
| 3. Examples and solution models | 25 | 1547 |
| 4. Code packages | 31 | 218 |
| 5. Apps | 22 | 88 |
| 8. Documentation | 21 | 111 |
| **Total (non-generated)** | **108** | **2073** |

### Counts by symbol (line hits; a line may match multiple symbols)

| Symbol | Hits | Primary carrier |
|---|---:|---|
| `logical_type` | 312 | LogicalAttribute |
| `LogicalDataTypeEnum` | 7 | schema enum |
| `format_pattern` | 5 | LogicalAttribute |
| `value_set_ref` | 7 | LogicalAttribute |
| `unit_code` | 29 | LogicalAttribute (Wave 2) |
| `currency_attribute_ref` | 29 | LogicalAttribute (Wave 2) |
| `timezone_policy` | 36 | LogicalAttribute (Wave 2) |
| `temporal_semantics` | 5 | LogicalAttribute (Wave 2) |
| `default_value` | 5 | LogicalAttribute |
| `derived_expression` | 13 | LogicalAttribute |
| `identity_rule` | 65 | LogicalEntity |
| `business_key_kind` | 57 | LogicalEntity |
| `key_attribute_refs` | 58 | ConceptualEntity + LogicalEntity |
| `definition_source_ref` | 754 | HasDefinition (all mixins) |
| `definition_rationale` | 17 | HasDefinition |
| `scoped_definitions` | 23 | HasDefinition |
| `genesis_kind` | 213 | ConceptualEntity |
| `external_class_refs` | 146 | ConceptualEntity |
| `conceptual_alignment_status` | 75 | LogicalEntity |
| `alignment_rationale` | 63 | LogicalEntity |
| `isolation_rationale` | 14 | LogicalEntity |
| `business_importance` | 151 | HasBusinessClassification |
| `HasBusinessClassification` | 15 | mixin class |
| `HasGovernanceClassification` | 24 | mixin on LogicalAttribute |
| `HasPolicyBindings` | 25 | mixin on LogicalAttribute |

---

## Per-symbol usage inventory

### `logical_type` (312 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 134, 437 | schema definition | - logical_type |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 56, 88 | model data | logical_type: identifier |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 444, 446 | model data | target_slot: logical_type |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1587-1588, 2814 | model data | logical_type: |
| `model-assets/implementations/imports/client-accounts-csv-draft/0.1/draft-model.yaml` | 21, 26 | model data | logical_type: identifier |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 42, 53, 64, 75, 86, 97, 108, 119, 130, 141, … (+48 more; last 714) | model data | logical_type: identifier |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 42, 53, 64, 75, 86, 117, 128, 159, 170, 203, … (+58 more; last 1013) | model data | logical_type: identifier |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 42, 53, 64, 75, 86, 97, 108, 119, 130, 141, … (+32 more; last 555) | model data | logical_type: identifier |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 42, 53, 64, 75, 86, 117, 128, 139, 150, 161, … (+30 more; last 600) | model data | logical_type: identifier |
| `model-assets/transformations/README.md` | 47 | model data | - `dams-logical-attribute-rename-type.yaml` — `logical_type` → `attribute_type` |
| `model-assets/transformations/dams-logical-attribute-rename-type.yaml` | 7, 13, 18, 28 | model data | Fixture migration — rename LogicalAttribute.logical_type to |
| `model-assets/transformations/samples/dams_logical_attribute_sample.json` | 4 | model data | "logical_type": "string" |
| `model-assets/transformations/schemas/dams_logical_attribute_source.yaml` | 21 | model data | logical_type: |
| `model-assets/transformations/schemas/dams_logical_attribute_target.yaml` | 5, 22 | model data | Target slice after renaming logical_type → attribute_type. |
| `packages/drawdb-adapter/src/moex_drawdb/patch.py` | 169, 192-193, 206, 209, 248, 687 | ingest/mapper | "logical_type": ltype, |
| `packages/drawdb-adapter/tests/test_round_trip.py` | 27, 34, 47 | test | "logical_type": "identifier", |
| `packages/linkml-tooling/tests/test_dams_slice_migrations.py` | 82, 84 | test | assert "logical_type" not in preview.preview_payload |
| `packages/specification-dams/src/moex_dams/projection/dbml.py` | 165, 181 | projection | ctype = _ident(attr.get("logical_type"), fallback="string") |
| `packages/specification-dams/src/moex_dams/projection/er_scene.py` | 169, 172, 177 | projection | ctype = _ident(attr.get("logical_type"), fallback="string") |
| `packages/specification-dams/src/moex_dams/projection/mermaid_er.py` | 264, 267, 273 | projection | ctype = _ident(attr.get("logical_type"), fallback="string") |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1090 | validator | ltype = str(el.get("logical_type") or "") |
| `packages/specification-dams/tests/test_cascade_resolver.py` | 41, 51, 75 | test | "logical_type": "string", |
| `packages/specification-dams/tests/test_dbml_projection.py` | 26, 32, 44, 50 | test | "logical_type": "identifier", |
| `packages/specification-dams/tests/test_definition_resolver.py` | 84 | test | "logical_type": "string", |
| `packages/specification-dams/tests/test_er_scene_layout.py` | 29, 36, 47, 53, 126 | test | "logical_type": "identifier", |
| `packages/specification-dams/tests/test_formal_checks.py` | 391, 393, 557, 624, 688 | test | data["logical_entities"][0]["attributes"][0].pop("logical_type", None) |
| `packages/specification-dams/tests/test_mermaid_er_projection.py` | 27, 34, 46, 52, 65, 77 | test | "logical_type": "identifier", |
| `packages/specification-dams/tests/test_semantic_diff.py` | 102 | test | "logical_type": "string", |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py` | 241, 250 | ingest/mapper | logical_type = profile.map_type(_opt_str(row.get("type")), is_pk=is_pk) |
| `packages/standard-linkml/tests/test_mapper.py` | 39, 44, 46 | test | assert client_id["logical_type"] == "identifier" |
| `apps/api/src/moex_model_api/yaml_mutate.py` | 140-141, 143, 175, 196 | api mutate | logical_type = str(attr.get("logical_type") or "").strip() |
| `apps/api/tests/test_api.py` | 230 | test | "logical_type": "string", |
| `apps/api/tests/test_transform_run.py` | 54 | test | assert any("entity_type" in s or "logical_type" in s for s in body["lost_semanti |
| `apps/api/tests/test_yaml_mutate.py` | 26, 54 | test | logical_type: identifier |
| `apps/viewer/static/viewer.js` | 4117 | viewer | rangeTd.textContent = attrs.logical_type \|\| attrs.native_type \|\| attrs.range |
| `apps/viewer/tests/test_normalizers.py` | 310, 331 | test | "logical_type": "identifier", |
| `apps/web/src/api/types.ts` | 84, 113 | web form | logical_type: string; |
| `apps/web/src/components/EntityForms.test.tsx` | 22 | test | logical_type: identifier |
| `apps/web/src/components/EntityForms.tsx` | 11, 43, 62, 159, 169, 228, 265, 283, 417, 517 | web form | logical_type: string; |
| `apps/web/src/model/yamlMutate.test.ts` | 13 | test | logical_type: identifier |
| `apps/web/src/model/yamlMutate.ts` | 264, 267, 281, 317 | web form | const logicalType = String(attr.logical_type \|\| "").trim(); |
| `docs/IMPLEMENTATION_PLAN.md` | 648 | docs | **Progress (2026-09-28, CLI-first + 7b + enrich/migrations + Workbench transform |
| `docs/architecture/uml/01-core-data-model.puml` | 60 | docs | +logical_type : LogicalDataTypeEnum [1] |
| `docs/architecture/uml/02-solution-model-governance.puml` | 71 | docs | +logical_type : LogicalDataTypeEnum [1] |

### `LogicalDataTypeEnum` (7 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 438 | schema definition | range: LogicalDataTypeEnum |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml` | 243 | schema definition | LogicalDataTypeEnum: |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 637-638, 1590 | model data | LogicalDataTypeEnum: |
| `docs/architecture/uml/01-core-data-model.puml` | 60 | docs | +logical_type : LogicalDataTypeEnum [1] |
| `docs/architecture/uml/02-solution-model-governance.puml` | 71 | docs | +logical_type : LogicalDataTypeEnum [1] |

### `format_pattern` (5 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 140, 454 | schema definition | - format_pattern |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1616-1617, 2820 | model data | format_pattern: |

### `value_set_ref` (7 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 139, 452 | schema definition | - value_set_ref |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1612-1613, 2819 | model data | value_set_ref: |
| `docs/architecture/uml/01-core-data-model.puml` | 63, 185 | docs | +value_set_ref : uri [0..1] |

### `unit_code` (29 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 145, 482 | schema definition | - unit_code |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 1021 | model data | remediation: Для decimal/datetime при необходимости добавьте currency_attribute_ |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1666-1667, 2825 | model data | unit_code: |
| `model-assets/implementations/solutions/crm/publications/vertical_slice.json` | 4531, 4539, 4547, 6264, 6276, 6288, 11012, 11025, 11038 | model data | "message": "LogicalAttribute \"dams:logical/crm/LEAD/ModifiedOn\" is datetime wi |
| `model-assets/implementations/solutions/esed/publications/vertical_slice.json` | 5636, 5644, 5652, 5660, 7069, 7081, 7093, 7105, 12528, 12541, 12554, 12567 | model data | "message": "LogicalAttribute \"dams:logical/esed/document/register_date\" is dat |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1092, 1103 | validator | _filled(el.get("unit_code")) or _filled(el.get("currency_attribute_ref")) |

### `currency_attribute_ref` (29 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 146, 485 | schema definition | - currency_attribute_ref |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 1021 | model data | remediation: Для decimal/datetime при необходимости добавьте currency_attribute_ |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1671-1672, 2826 | model data | currency_attribute_ref: |
| `model-assets/implementations/solutions/crm/publications/vertical_slice.json` | 4531, 4539, 4547, 6264, 6276, 6288, 11012, 11025, 11038 | model data | "message": "LogicalAttribute \"dams:logical/crm/LEAD/ModifiedOn\" is datetime wi |
| `model-assets/implementations/solutions/esed/publications/vertical_slice.json` | 5636, 5644, 5652, 5660, 7069, 7081, 7093, 7105, 12528, 12541, 12554, 12567 | model data | "message": "LogicalAttribute \"dams:logical/esed/document/register_date\" is dat |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1092, 1103 | validator | _filled(el.get("unit_code")) or _filled(el.get("currency_attribute_ref")) |

### `timezone_policy` (36 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 147, 488 | schema definition | - timezone_policy |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 1022 | model data | timezone_policy. |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1676-1677, 2827 | model data | timezone_policy: |
| `model-assets/implementations/solutions/crm/publications/vertical_slice.json` | 4531, 4539, 4547, 6262, 6264, 6274, 6276, 6286, 6288, 11012, 11025, 11038 | model data | "message": "LogicalAttribute \"dams:logical/crm/LEAD/ModifiedOn\" is datetime wi |
| `model-assets/implementations/solutions/esed/publications/vertical_slice.json` | 5636, 5644, 5652, 5660, 7067, 7069, 7079, 7081, 7091, 7093, … (+6 more; last 12567) | model data | "message": "LogicalAttribute \"dams:logical/esed/document/register_date\" is dat |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1111, 1117 | validator | if ltype == "datetime" and not _filled(el.get("timezone_policy")): |

### `temporal_semantics` (5 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 148, 491 | schema definition | - temporal_semantics |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1681-1682, 2828 | model data | temporal_semantics: |

### `default_value` (5 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 141, 456 | schema definition | - default_value |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1620-1621, 2821 | model data | default_value: |

### `derived_expression` (13 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 142, 458 | schema definition | - derived_expression |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 506 | model data | remediation: Добавьте field_mapping и/или derived_expression, либо укажите mappi |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1624-1625, 2822 | model data | derived_expression: |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 829-830, 848, 856, 868, 877 | validator | # derived may use derived_expression instead |
| `packages/specification-dams/tests/test_formal_checks.py` | 431 | test | attr["derived_expression"] = "upper(party_id)" |

### `identity_rule` (65 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 112, 460 | schema definition | - identity_rule |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml` | 96 | schema definition | description: Технический ключ реализации; не заменяет identity_rule. |
| `model-assets/specifications/moex-dams/0.1/requirements/README.md` | 30, 46 | model data | **ADR-019 ≠ body assess.** Missing `identity_rule`, `ownership`, or |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 39, 73 | model data | identity_rule: >- |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 300, 319 | model data | description: identity_rule и ключ; surrogate alone insufficient. |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 393, 1628-1629, 2788 | model data | description: Технический ключ реализации; не заменяет identity_rule. |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 228, 516, 724 | model data | identity_rule: Идентичность определяется первичным ключом сущности в контуре ИТ- |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 96, 138, 180, 235, 532, 620, 696, 749, 793, 903, 970, 1023 | model data | identity_rule: Идентичность определяется первичным ключом сущности в контуре ИТ- |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 327, 481, 523, 565 | model data | identity_rule: Идентичность определяется первичным ключом сущности в контуре ИТ- |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 55 | model data | identity_rule: > |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 96, 182, 314, 425, 478, 555, 610 | model data | identity_rule: Идентичность определяется первичным ключом сущности в контуре ИТ- |
| `model-assets/specifications/moex-dams/0.1/publication-requirements.yaml` | 94 | model data | identity_rule / ownership / mapping_coverage body fields. |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 583, 588, 612, 627-630 | validator | if not _filled(el.get("identity_rule")): |
| `packages/specification-dams/tests/test_formal_checks.py` | 323, 613, 678 | test | ent.pop("identity_rule", None) |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/enrich.py` | 45 | ingest/mapper | ent["identity_rule"] = defaults.identity_rule.strip() |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 175 | ingest/mapper | identity_rule: str = ( |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 55 | ingest/mapper | identity_rule: > |
| `apps/viewer/tests/test_publication_contract_phase2.py` | 418 | test | # Minimal entity: no identity_rule, ownership, or mapping_coverage_status |
| `docs/adr/ADR-013-specification-requirements-catalog.md` | 46, 52, 67, 79 | docs | доказывает identity_rule или classification. |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 178, 237, 580, 582, 604 | docs | - identity_rule; |
| `docs/architecture/uml/01-core-data-model.puml` | 51 | docs | +identity_rule : string [0..1] |

### `business_key_kind` (57 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 113, 464 | schema definition | - business_key_kind |
| `model-assets/specifications/moex-dams/0.1/requirements/README.md` | 45 | model data | - Reject or warn `business_key_kind: surrogate` without `key_attribute_refs` |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 42, 75 | model data | business_key_kind: local |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 319 | model data | remediation: Добавьте identity_rule и business_key_kind и/или key_attribute_refs |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1635-1636, 2789 | model data | business_key_kind: |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 227, 515, 723 | model data | business_key_kind: surrogate |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 95, 137, 179, 234, 531, 619, 695, 748, 792, 902, 969, 1022 | model data | business_key_kind: surrogate |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 326, 480, 522, 564 | model data | business_key_kind: surrogate |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 54 | model data | business_key_kind: surrogate |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 95, 181, 313, 424, 477, 554, 609 | model data | business_key_kind: surrogate |
| `packages/specification-dams/src/moex_dams/projection/er_scene.py` | 174, 178, 251 | projection | or bool(attr.get("business_key_kind")) |
| `packages/specification-dams/src/moex_dams/projection/mermaid_er.py` | 269, 274, 312 | projection | or bool(attr.get("business_key_kind")) |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 595, 603 | validator | kind = el.get("business_key_kind") |
| `packages/specification-dams/tests/test_formal_checks.py` | 324, 614, 679 | test | ent["business_key_kind"] = "surrogate" |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/enrich.py` | 44, 51 | ingest/mapper | ent["business_key_kind"] = defaults.business_key_kind |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 174 | ingest/mapper | business_key_kind: str = "surrogate" |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 54 | ingest/mapper | business_key_kind: surrogate |
| `docs/adr/ADR-013-specification-requirements-catalog.md` | 79 | docs | **Wave 1 surrogate policy:** `business_key_kind: surrogate` + `identity_rule` |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 179, 245, 588, 604 | docs | - business_key_kind; |
| `docs/architecture/uml/01-core-data-model.puml` | 52 | docs | +business_key_kind : BusinessKeyKindEnum [0..1] |

### `key_attribute_refs` (58 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 82, 110, 370 | schema definition | - key_attribute_refs |
| `model-assets/specifications/moex-dams/0.1/requirements/README.md` | 45 | model data | - Reject or warn `business_key_kind: surrogate` without `key_attribute_refs` |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 43, 76 | model data | key_attribute_refs: |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 319 | model data | remediation: Добавьте identity_rule и business_key_kind и/или key_attribute_refs |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1488-1489, 2754, 2786 | model data | key_attribute_refs: |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 223, 511, 719 | model data | key_attribute_refs: |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 91, 133, 175, 230, 527, 615, 691, 744, 788, 898, 965, 1018 | model data | key_attribute_refs: |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 322, 476, 518, 560 | model data | key_attribute_refs: |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 91, 177, 309, 420, 473, 550, 605 | model data | key_attribute_refs: |
| `packages/specification-dams/src/moex_dams/application/diff.py` | 42 | transformation | "key_attribute_refs", |
| `packages/specification-dams/src/moex_dams/projection/er_common.py` | 43 | projection | for ref in entity.get("key_attribute_refs") or []: |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 596, 604 | validator | keys = el.get("key_attribute_refs") or [] |
| `packages/specification-dams/src/moex_dams/rules/structural.py` | 50, 63 | validator | key_refs = entity.get("key_attribute_refs") or [] |
| `packages/specification-dams/tests/test_formal_checks.py` | 325 | test | ent.pop("key_attribute_refs", None) |
| `packages/standard-linkml/README.md` | 87 | ingest/mapper | - Attributes → nested `LogicalAttribute` (`pk` → `key_attribute_refs`, types via |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py` | 213, 257 | ingest/mapper | "key_attribute_refs": [], |
| `packages/standard-linkml/tests/test_mapper.py` | 35 | test | assert client["key_attribute_refs"] == [ |
| `apps/viewer/static/viewer.js` | 4698 | viewer | "key_attribute_refs", |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 512 | docs | - key_attribute_refs |
| `docs/adr/ADR-013-specification-requirements-catalog.md` | 67, 80 | docs | \| Surrogate без `key_attribute_refs` (при наличии `identity_rule`) \| Allowed \ |
| `docs/adr/ADR-029-cdm-from-er-sketch-and-realization.md` | 48 | docs | **No `ConceptualAttribute` class.** Slot `key_attribute_refs` remains unused for |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 246, 589 | docs | - key_attribute_refs |
| `docs/architecture/uml/01-core-data-model.puml` | 35, 53, 177 | docs | +key_attribute_refs : uriorcurie [0..*] |

### `definition_source_ref` (754 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 93, 122, 196 | schema definition | definition_source_ref (ontology class or GlossaryTerm) per ADR-025. |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 105, 109, 209 | schema definition | definition_source_ref означает наследование; заданный description — |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml` | 428 | schema definition | definition_source_ref, or single conceptual_entity_refs inheritance. |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 231 | model data | Задайте description (own), либо definition_source_ref / единственный |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 948, 1293-1294, 2656, 2665, 2764, 2797, 2880 | model data | definition_source_ref, or single conceptual_entity_refs inheritance. |
| `model-assets/implementations/solutions/crm/publications/vertical_slice.json` | 5075, 5083, 5091, 5099, 5107, 5115, 5123, 5131, 5139, 5147, … (+173 more; last 12676) | model data | "message": "LogicalEntity \"dams:logical/crm/CONTACT\" description equals title  |
| `model-assets/implementations/solutions/esed/publications/vertical_slice.json` | 6412, 6420, 6428, 6436, 6444, 6452, 6460, 6468, 6476, 6484, … (+230 more; last 14816) | model data | "message": "LogicalEntity \"dams:logical/esed/attorney_check_info\" description  |
| `model-assets/implementations/solutions/mdm/publications/vertical_slice.json` | 3823, 3831, 3839, 3847, 3855, 3863, 3871, 3879, 3887, 3895, … (+122 more; last 9486) | model data | "message": "LogicalEntity \"dams:logical/mdm/ENTERPRISE\" description equals tit |
| `model-assets/implementations/solutions/ucd/publications/vertical_slice.json` | 3808, 3816, 3824, 3832, 3840, 3848, 3856, 3864, 3872, 3880, … (+131 more; last 9079) | model data | "message": "LogicalEntity \"dams:logical/ucd/AGREEMENT\" description equals titl |
| `packages/specification-dams/src/moex_dams/rules/definitions.py` | 3, 183, 283, 323, 355, 387, 405, 447 | validator | YAML stores declared description / definition_source_ref / scoped_definitions. |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1440, 1449, 1461 | validator | "or inherit via definition_source_ref (ADR-025)." |
| `packages/specification-dams/tests/test_cmd_entity_metamodel.py` | 289, 320 | test | "definition_source_ref": "fibo:LegalPerson", |
| `packages/specification-dams/tests/test_definition_resolver.py` | 57, 133, 186, 209, 213, 364 | test | "definition_source_ref": "fibo:LegalPerson", |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 100, 151, 194, 205, 221 | viewer | "definition_source_ref", |
| `apps/viewer/src/moex_publication_viewer/normalizers/model_glossary_projection.py` | 28 | viewer | source = el.get("definition_source_ref") |
| `apps/viewer/tests/test_implementation_glossary.py` | 95 | test | "definition_source_ref": "dams:concept/A", |
| `docs/LinkML_Glossary_DAMS.md` | 59 | docs | \| `HasDefinition` \| Эталонное определение (ADR-025): `description` = own `skos |
| `docs/adr/ADR-025-definition-cascade-and-glossary.md` | 40, 54, 78, 80, 86, 104, 130 | docs | `definition_source_ref`. |
| `docs/adr/ADR-026-cmd-entity-metamodel.md` | 117 | docs | When resolving `definition_source_ref` to an external term, **exactness** is |
| `docs/adr/ADR-027-glossary-term-relations.md` | 33, 69, 116 | docs | 3. conflated with `glossary_term_refs`, `definition_source_ref`, or |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 514 | docs | - разрешимое эталонное определение (ADR-025): own `description`, либо наследован |
| `docs/architecture/ontology-catalog.md` | 111 | docs | \| Источник унаследованного / adapted определения \| `definition_source_ref` (AD |
| `docs/superpowers/plans/2026-10-05-viewer-inline-edit.md` | 33 | docs | - Не править идентификаторы (`id`, `name`, `element_id`) и поля ADR-025 (`defini |
| `docs/superpowers/specs/2026-10-05-viewer-inline-edit-design.md` | 18 | docs | (`definition_source_ref`, `definition_rationale`, `scoped_definitions`). |

### `definition_rationale` (17 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 110, 214 | schema definition | - definition_rationale |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1301-1302, 2666 | model data | definition_rationale: |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 1451-1452, 1461, 1465 | validator | isinstance(el.get("definition_rationale"), str) |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 101, 545 | viewer | "definition_rationale", |
| `apps/viewer/static/viewer.js` | 4260-4261 | viewer | if (attrs.definition_rationale) { |
| `docs/adr/ADR-025-definition-cascade-and-glossary.md` | 104, 120 | docs | - Mixin `HasDefinition`: `definition_source_ref`, `definition_rationale`, |
| `docs/superpowers/plans/2026-10-05-viewer-inline-edit.md` | 33 | docs | - Не править идентификаторы (`id`, `name`, `element_id`) и поля ADR-025 (`defini |
| `docs/superpowers/specs/2026-10-05-viewer-inline-edit-design.md` | 18 | docs | (`definition_source_ref`, `definition_rationale`, `scoped_definitions`). |

### `scoped_definitions` (23 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 106, 111, 219 | schema definition | own (опционально adapted from source). scoped_definitions — контекстные |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1309-1310, 2658, 2667 | model data | scoped_definitions: |
| `packages/specification-dams/src/moex_dams/rules/definitions.py` | 3, 301, 488, 490 | validator | YAML stores declared description / definition_source_ref / scoped_definitions. |
| `packages/specification-dams/tests/test_definition_resolver.py` | 241, 332 | test | "scoped_definitions": [ |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 102, 555 | viewer | "scoped_definitions", |
| `apps/viewer/static/viewer.js` | 4297-4298 | viewer | const scoped = Array.isArray(attrs.scoped_definitions) |
| `docs/LinkML_Glossary_DAMS.md` | 59 | docs | \| `HasDefinition` \| Эталонное определение (ADR-025): `description` = own `skos |
| `docs/adr/ADR-025-definition-cascade-and-glossary.md` | 77, 105 | docs | 1. Matching `scoped_definitions` for `scope` → most specific; mode `scoped`. |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 514 | docs | - разрешимое эталонное определение (ADR-025): own `description`, либо наследован |
| `docs/superpowers/plans/2026-10-05-viewer-inline-edit.md` | 33 | docs | - Не править идентификаторы (`id`, `name`, `element_id`) и поля ADR-025 (`defini |
| `docs/superpowers/specs/2026-10-05-viewer-inline-edit-design.md` | 18 | docs | (`definition_source_ref`, `definition_rationale`, `scoped_definitions`). |

### `genesis_kind` (213 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 86, 390, 402 | schema definition | - genesis_kind |
| `model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml` | 185-186, 193, 198 | model data | (genesis_kind=external с external_class_refs и match_kind), либо является |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml` | 26, 40, 57, 73, 90, 104, 115, 131, 142, 158, … (+72 more; last 1014) | model data | genesis_kind: native |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/publications/model_glossary.json` | 12, 28, 44, 60, 76, 194, 210, 294, 310, 343, … (+72 more; last 2399) | model data | "genesis_kind": "native", |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/publish.yaml` | 63, 68, 93 | model data | - genesis_kind |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1519-1520, 1530, 2758 | model data | genesis_kind: |
| `packages/specification-dams/src/moex_dams/rules/conceptual_entity.py` | 118, 130, 244, 248, 257, 261, 271, 274 | validator | """Validate entity_tier / dependency_kind / genesis_kind (ADR-026).""" |
| `packages/specification-dams/src/moex_dams/rules/glossary.py` | 57 | validator | "genesis_kind": el.get("genesis_kind"), |
| `packages/specification-dams/tests/test_cmd_entity_metamodel.py` | 50, 59, 68, 77, 91, 209, 218, 252, 268, 377 | test | "genesis_kind": "native", |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 108, 561 | viewer | "genesis_kind", |
| `apps/viewer/src/moex_publication_viewer/normalizers/model_glossary_projection.py` | 47 | viewer | "genesis_kind": el.get("genesis_kind"), |
| `apps/viewer/static/viewer.js` | 2746, 4444 | viewer | // Origin (not genesis_kind) |
| `apps/viewer/tests/test_model_glossary_projection.py` | 19, 27 | test | "genesis_kind": "native", |
| `apps/viewer/tests/test_spec_glossary_tree.py` | 60, 171 | test | assert "genesis_kind" not in attrs |
| `docs/LinkML_Glossary_DAMS.md` | 69, 285 | docs | **Слоты `ConceptualEntity` (ADR-026):** `entity_tier` (primary/dependent), `depe |
| `docs/adr/ADR-023-governed-property-cascade.md` | 129 | docs | - ADR-026 (`entity_tier` / `genesis_kind` are structural metadata on ConceptualE |
| `docs/adr/ADR-024-unified-class-entity.md` | 26 | docs | 3. **Class hierarchy** uses asserted `subClassOf` (preview: `parent_local_name`) |
| `docs/adr/ADR-026-cmd-entity-metamodel.md` | 95 | docs | \| `genesis_kind` \| `external` \\| `native` \| |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 1225, 1240 | docs | (entity_tier, genesis_kind, external_class_refs, RelationTerm — ADR-026) |

### `external_class_refs` (146 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 87, 395 | schema definition | - external_class_refs |
| `model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml` | 177-178, 185, 187 | model data | Genesis and external_class_refs (ADR-026). external ⇔ ≥1 |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml` | 41, 3539 | model data | external_class_refs: |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/publications/model_glossary.json` | 14, 30, 46, 62, 78, 196, 212, 296, 312, 345, … (+72 more; last 2401) | model data | "external_class_refs": [], |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1527-1528, 2759 | model data | external_class_refs: |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-hierarchy-model.yaml` | 361 | model data | external_class_refs: |
| `packages/specification-dams/src/moex_dams/rules/conceptual_entity.py` | 131, 245, 258, 261, 270, 324, 328, 355, 384 | validator | ext_refs = el.get("external_class_refs") or [] |
| `packages/specification-dams/src/moex_dams/rules/definitions.py` | 154, 158, 359 | validator | """Return exactness from ConceptualEntity.external_class_refs (ADR-026). |
| `packages/specification-dams/src/moex_dams/rules/glossary.py` | 37, 59 | validator | for cref in el.get("external_class_refs") or []: |
| `packages/specification-dams/tests/test_cmd_entity_metamodel.py` | 269, 290, 321, 378 | test | "external_class_refs": [ |
| `apps/viewer/src/moex_publication_viewer/normalizers/hierarchy_projection.py` | 219, 223, 302, 356, 396, 399, 416 | viewer | # OWL stubs from external_class_refs |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 105, 558 | viewer | "external_class_refs", |
| `apps/viewer/static/viewer.js` | 2727, 4410-4411, 4417, 6688, 6715, 7324 | viewer | .concat(attrs.external_class_refs \|\| []); |
| `apps/viewer/tests/test_atlas_polish.py` | 118 | test | assert "external_class_refs" in align |
| `apps/viewer/tests/test_hierarchy_projection.py` | 145 | test | "external_class_refs": [ |
| `apps/viewer/tests/test_implementation_glossary.py` | 143, 332 | test | "external_class_refs": [ |
| `docs/LinkML_Glossary_DAMS.md` | 69, 281 | docs | **Слоты `ConceptualEntity` (ADR-026):** `entity_tier` (primary/dependent), `depe |
| `docs/adr/ADR-021-dams-implementation-profile-and-levels.md` | 45 | docs | \| `external_class_refs` \| Canonical ConceptualEntity → external class/term wit |
| `docs/adr/ADR-025-definition-cascade-and-glossary.md` | 83, 142 | docs | `ConceptualEntity.external_class_refs[].match_kind` when present (ADR-026), |
| `docs/adr/ADR-026-cmd-entity-metamodel.md` | 39, 96, 107, 110, 113, 118 | docs | Conceptual→external class uses `external_class_refs` / `aligns_with`, not those |
| `docs/adr/ADR-027-glossary-term-relations.md` | 69 | docs | \| **Model** (ADR-026) \| `parent_concept_ref` on `ConceptualEntity` \| Other en |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 1225, 1240 | docs | (entity_tier, genesis_kind, external_class_refs, RelationTerm — ADR-026) |

### `conceptual_alignment_status` (75 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 114, 466 | schema definition | - conceptual_alignment_status |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 45, 78 | model data | conceptual_alignment_status: local-only |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 364 | model data | remediation: Укажите conceptual_entity_refs (aligned) либо conceptual_alignment_ |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1639-1640, 2790 | model data | conceptual_alignment_status: |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 229, 517, 725 | model data | conceptual_alignment_status: aligned |
| `model-assets/implementations/solutions/crm/publish.yaml` | 41, 44 | model data | - conceptual_alignment_status |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 97, 139, 181, 236, 533, 621, 697, 750, 794, 904, 971, 1024 | model data | conceptual_alignment_status: aligned |
| `model-assets/implementations/solutions/esed/publish.yaml` | 40, 43 | model data | - conceptual_alignment_status |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 328, 482, 524, 566 | model data | conceptual_alignment_status: aligned |
| `model-assets/implementations/solutions/mdm/publish.yaml` | 41, 44 | model data | - conceptual_alignment_status |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 58 | model data | conceptual_alignment_status: pending |
| `model-assets/implementations/solutions/ucd/publish.yaml` | 41, 44 | model data | - conceptual_alignment_status |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 97, 183, 315, 426, 479, 556, 611 | model data | conceptual_alignment_status: aligned |
| `packages/specification-dams/src/moex_dams/rules/definitions.py` | 319 | validator | alignment = str(element.get("conceptual_alignment_status") or "") |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 656, 734, 748, 781 | validator | status = str(el.get("conceptual_alignment_status") or "") |
| `packages/specification-dams/tests/test_definition_resolver.py` | 75, 198, 228, 299 | test | "conceptual_alignment_status": "aligned", |
| `packages/specification-dams/tests/test_formal_checks.py` | 342, 351, 363, 378, 612, 677 | test | e["conceptual_alignment_status"] = "not-applicable" |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/enrich.py` | 46 | ingest/mapper | ent["conceptual_alignment_status"] = defaults.conceptual_alignment_status |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 179 | ingest/mapper | conceptual_alignment_status: str = "pending" |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/scaffold.py` | 63, 66 | ingest/mapper | "conceptual_alignment_status", |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 58 | ingest/mapper | conceptual_alignment_status: pending |
| `apps/viewer/src/moex_publication_viewer/normalizers/conceptual_entity_links_projection.py` | 28, 41 | viewer | alignment = entity.get("conceptual_alignment_status") |
| `apps/viewer/src/moex_publication_viewer/normalizers/implementation_glossary.py` | 104, 147 | viewer | "conceptual_alignment_status", |
| `apps/viewer/tests/test_conceptual_entity_links_projection.py` | 27, 41, 53 | test | "conceptual_alignment_status": "aligned", |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 647 | docs | conceptual_alignment_status: aligned |
| `docs/architecture/uml/01-core-data-model.puml` | 54 | docs | +conceptual_alignment_status : ConceptualAlignmentStatusEnum [0..1] |
| `docs/architecture/uml/02-solution-model-governance.puml` | 68 | docs | +conceptual_alignment_status : ConceptualAlignmentStatusEnum [0..1] |
| `docs/architecture/uml/03-external-semantics.puml` | 119 | docs | +conceptual_alignment_status : ConceptualAlignmentStatusEnum [0..1] |
| `docs/dev/solution-xlsx-import.md` | 94 | docs | - `conceptual_alignment_status: pending` + локальные realizes на stub-концепты — |

### `alignment_rationale` (63 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 115, 468 | schema definition | - alignment_rationale |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 46, 79 | model data | alignment_rationale: >- |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 341, 364 | model data | remediation: Добавьте хотя бы один атрибут либо для technical укажите isolation_ |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1643-1644, 2791 | model data | alignment_rationale: |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 230, 518, 726 | model data | alignment_rationale: CRM CONTACT — локальная проекция корпоративного Person (ФИО |
| `model-assets/implementations/solutions/crm/publish.yaml` | 42 | model data | - alignment_rationale |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 98, 140, 182, 237, 534, 622, 698, 751, 795, 905, 972, 1025 | model data | alignment_rationale: Проверка доверенности на карточке — характеристика Supporti |
| `model-assets/implementations/solutions/esed/publish.yaml` | 41 | model data | - alignment_rationale |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 329, 483, 525, 567 | model data | alignment_rationale: MDM ENTERPRISE — золотая запись ЮЛ; реализует LegalEntity ( |
| `model-assets/implementations/solutions/mdm/publish.yaml` | 42 | model data | - alignment_rationale |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 59 | model data | alignment_rationale: > |
| `model-assets/implementations/solutions/ucd/publish.yaml` | 42 | model data | - alignment_rationale |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 98, 184, 316, 427, 480, 557, 612 | model data | alignment_rationale: UCD AGREEMENT реализует корпоративный Agreement. |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 639, 658, 685, 717, 754 | validator | _filled(el.get("isolation_rationale")) or _filled(el.get("alignment_rationale")) |
| `packages/specification-dams/tests/test_definition_resolver.py` | 300 | test | alignment_rationale="local", |
| `packages/specification-dams/tests/test_formal_checks.py` | 343, 352, 364, 379 | test | e["alignment_rationale"] = "bypass" |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/enrich.py` | 47 | ingest/mapper | ent["alignment_rationale"] = defaults.alignment_rationale.strip() |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 180 | ingest/mapper | alignment_rationale: str = ( |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/scaffold.py` | 64 | ingest/mapper | "alignment_rationale", |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 59 | ingest/mapper | alignment_rationale: > |
| `apps/viewer/src/moex_publication_viewer/normalizers/conceptual_entity_links_projection.py` | 29, 44 | viewer | rationale = entity.get("alignment_rationale") |
| `apps/viewer/tests/test_conceptual_entity_links_projection.py` | 28, 42, 54 | test | "alignment_rationale": "Local stub + enterprise.", |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 635, 650, 1113 | docs | \| Статус \| `conceptual_entity_refs` \| `alignment_rationale` \| |
| `docs/architecture/uml/01-core-data-model.puml` | 55 | docs | +alignment_rationale : string [0..1] |

### `isolation_rationale` (14 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 116, 471 | schema definition | - isolation_rationale |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 341, 388 | model data | remediation: Добавьте хотя бы один атрибут либо для technical укажите isolation_ |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 1648-1649, 2792 | model data | isolation_rationale: |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 639, 761 | validator | _filled(el.get("isolation_rationale")) or _filled(el.get("alignment_rationale")) |
| `packages/specification-dams/tests/test_formal_checks.py` | 365, 380, 615, 725 | test | e.pop("isolation_rationale", None) |
| `docs/architecture/uml/01-core-data-model.puml` | 56 | docs | +isolation_rationale : string [0..1] |

### `business_importance` (151 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 66, 178 | schema definition | - business_importance |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml` | 137 | schema definition | entity_type, data_class, and business_importance. |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 36, 70 | model data | business_importance: high |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 255, 284, 286 | model data | description: entity_type, data_class, business_importance, governance. |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml` | 24, 37, 55, 68, 85, 102, 113, 126, 140, 153, … (+72 more; last 1022) | model data | business_importance: high |
| `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/publish.yaml` | 61 | model data | - business_importance |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 458, 1238-1239, 2614 | model data | to entity_type, data_class, and business_importance. |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 34, 245, 530 | model data | business_importance: medium |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 34, 109, 151, 195, 250, 547, 634, 709, 764, 808, 919, 983 | model data | business_importance: medium |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 34, 342, 494, 536 | model data | business_importance: medium |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 48 | model data | business_importance: medium |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 34, 109, 197, 330, 438, 493, 570 | model data | business_importance: medium |
| `packages/specification-dams/tests/test_definition_resolver.py` | 50, 60 | test | "business_importance": "high", |
| `packages/specification-dams/tests/test_formal_checks.py` | 610, 675 | test | "business_importance": "high", |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py` | 120, 159, 182, 211 | ingest/mapper | "business_importance": defaults.business_importance, |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/profile.py` | 84 | ingest/mapper | business_importance: str = "medium" |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 167, 351 | ingest/mapper | business_importance: str = "medium" |
| `packages/standard-linkml/templates/er-dictionary.profile.yaml` | 99 | ingest/mapper | business_importance: medium |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 48 | ingest/mapper | business_importance: medium |
| `packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml` | 96 | test | business_importance: medium |
| `docs/LinkML_Glossary_DAMS.md` | 56, 69, 203 | docs | \| `HasBusinessClassification` \| Роль в бизнесе: `entity_type`, `data_class`, ` |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 303, 535, 637, 665 | docs | \| `business_importance` \| `LogicalEntity` \| `high`, `medium`, `low` \| Бизнес |
| `docs/adr/ADR-023-governed-property-cascade.md` | 77 | docs | **Not in cascade:** `entity_type`, `data_class`, `business_importance` |
| `docs/adr/ADR-026-cmd-entity-metamodel.md` | 30, 84, 143 | docs | to `business_importance` and `entity_type`. |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 521, 532, 540, 1239 | docs | - `business_importance`; |

### `HasBusinessClassification` (15 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 77, 99 | schema definition | - HasBusinessClassification |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 60 | schema definition | HasBusinessClassification: |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 2606-2607, 2750, 2776 | model data | HasBusinessClassification: |
| `docs/LinkML_Glossary_DAMS.md` | 56, 277 | docs | \| `HasBusinessClassification` \| Роль в бизнесе: `entity_type`, `data_class`, ` |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 320, 503, 530 | docs | - `HasBusinessClassification` — entity type, data class, importance; |
| `docs/adr/ADR-026-cmd-entity-metamodel.md` | 21 | docs | today’s slots (`parent_concept_ref`, `HasBusinessClassification`, |
| `docs/architecture/uml/01-core-data-model.puml` | 27 | docs | Further mixins (HasOwnership, HasBusinessClassification, |
| `docs/architecture/uml/all_model_modules.puml` | 126 | docs | HasBusinessClassification, |

### `HasGovernanceClassification` (24 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 36, 100, 128, 217 | schema definition | - HasGovernanceClassification |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 68 | schema definition | HasGovernanceClassification: |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-technical.yaml` | 55 | schema definition | - HasGovernanceClassification |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 2615-2616, 2713, 2777, 2809, 2911, 2996 | model data | HasGovernanceClassification: |
| `docs/LinkML_Glossary_DAMS.md` | 57, 277, 297 | docs | \| `HasGovernanceClassification` \| Базовая маркировка: `governance_classificati |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 321, 504, 537 | docs | - `HasGovernanceClassification` — access level, special classification terms, so |
| `docs/adr/ADR-023-governed-property-cascade.md` | 19 | docs | Governance mixins (`HasOwnership`, `HasGovernanceClassification`, `HasPolicyBind |
| `docs/architecture/uml/01-core-data-model.puml` | 28 | docs | HasGovernanceClassification, HasPolicyBindings, HasProvenance) |
| `docs/architecture/uml/all_model_modules.puml` | 127 | docs | HasGovernanceClassification, |
| `docs/migration/technical-asset-inventory.md` | 17, 204 | docs | \| `PhysicalObject` class \| `model-assets/specifications/moex-dams/0.1/schemas/ |

### `HasPolicyBindings` (25 hits)

| File | Line(s) | Usage type | Context |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-analytics.yaml` | 22 | schema definition | - HasPolicyBindings |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 37, 101, 129, 218 | schema definition | - HasPolicyBindings |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml` | 81 | schema definition | HasPolicyBindings: |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-technical.yaml` | 56 | schema definition | - HasPolicyBindings |
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 2630-2631, 2714, 2778, 2810, 2912, 2997, 3261 | model data | HasPolicyBindings: |
| `docs/LinkML_Glossary_DAMS.md` | 58, 111, 277 | docs | \| `HasPolicyBindings` \| `policy_refs`: absent = inherit; present list (в т.ч.  |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 322, 505 | docs | - `HasPolicyBindings` — ссылки на применимые политики; |
| `docs/adr/ADR-023-governed-property-cascade.md` | 19 | docs | Governance mixins (`HasOwnership`, `HasGovernanceClassification`, `HasPolicyBind |
| `docs/architecture/uml/01-core-data-model.puml` | 28 | docs | HasGovernanceClassification, HasPolicyBindings, HasProvenance) |
| `docs/architecture/uml/all_model_modules.puml` | 128 | docs | HasPolicyBindings, HasProvenance |
| `docs/migration/technical-asset-inventory.md` | 17, 206 | docs | \| `PhysicalObject` class \| `model-assets/specifications/moex-dams/0.1/schemas/ |

---

## Special findings

### ConceptualEntity.`key_attribute_refs` — real data vs schema

| Finding | Detail |
|---|---|
| Enterprise conceptual model | `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml` — **нет** ни одного заполненного `key_attribute_refs` на `ConceptualEntity` (только `genesis_kind` / `external_class_refs`). |
| Hierarchy spec dump | `moex-dams-full.yaml:1488-1489` — мета-запись слота (`name: key_attribute_refs`), не бизнес-данные. |
| LogicalEntity (solution models) | Все фактические значения `key_attribute_refs` — списки `dams:logical/{solution}/...` (см. crm/esed/mdm/ucd solution YAML, example `it-solution-model.example.yaml`). |
| Validator | `packages/specification-dams/src/moex_dams/rules/structural.py` — проверяет, что refs ∈ attributes entity. |
| Semantic diff | `key_attribute_refs` в `_SKIP_KEYS` (`diff.py:42`) — изменения ключей не классифицируются отдельно (остаются в graph edges). |

### LogicalAttribute governance mixins (ADR-023)

| Mixin | On LogicalAttribute | In code / rules |
|---|---|---|
| `HasBusinessClassification` | **No** (only ConceptualEntity, LogicalEntity) | `formal_checks`, cascade — entity-level `business_importance` |
| `HasGovernanceClassification` | **Yes** (`moex-core.yaml:128`) | `cascade.py`, `formal_checks.py`, projections inherit display |
| `HasPolicyBindings` | **Yes** (`moex-core.yaml:129`) | `cascade.py`, policy full-replace semantics ADR-023 |

### `packages/specification-dams`: ChangeCategory & deprecated

| Location | Relevance to this migration |
|---|---|
| `application/diff.py` | Property deltas on `logical_type`, `identity_rule`, etc. → `ChangeCategory.BREAKING` (`DAMS-DIFF-PROP`) unless doc/gov-only; `key_attribute_refs` skipped in scalar diff. |
| `application/ontology_report.py` | Structural add/remove → BREAKING / NON_BREAKING. |
| `tests/test_semantic_diff.py`, `test_ontology_report.py` | Fixture coverage for categories; no slot-specific deprecation map. |
| `deprecated` | Only requirement lifecycle fixture (`tests/fixtures/requirements/status-showcase.yaml`); **no** deprecated markers for LogicalAttribute slots in specification-dams. |
| `packages/linkml-tooling/tests/test_dams_slice_migrations.py` | Slice preview lists `logical_type` / `LogicalAttribute.logical_type` as **lost_semantics** when slicing — relevant if ConceptualProperty extraction uses DAMS slice. |

---

## Preliminary ConceptualProperty candidates (no objects created)

### identifying (from `LogicalEntity.key_attribute_refs`)

| Solution | Attribute id | Name |
|---|---|---|
| crm | `dams:logical/crm/CONTACT/Id` | Id |
| crm | `dams:logical/crm/CUSTOMER/Id` | Id |
| crm | `dams:logical/crm/LEAD/ApplicationId` | ApplicationId |
| esed | `dams:logical/esed/attorney_check_info/instance_id` | instance_id |
| esed | `dams:logical/esed/common_state/state_id` | state_id |
| esed | `dams:logical/esed/common_type/type_id` | type_id |
| esed | `dams:logical/esed/division/division_id` | division_id |
| esed | `dams:logical/esed/document/document_id` | document_id |
| esed | `dams:logical/esed/employee/employee_id` | employee_id |
| esed | `dams:logical/esed/file/id` | id |
| esed | `dams:logical/esed/file_binary/id` | id |
| esed | `dams:logical/esed/instance/instance_id` | instance_id |
| esed | `dams:logical/esed/organization/organization_id` | organization_id |
| esed | `dams:logical/esed/organization_employee/employee_id` | employee_id |
| esed | `dams:logical/esed/universal_item/item_id` | item_id |
| mdm | `dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID` | ENTERPRISE_ID |
| mdm | `dams:logical/mdm/PERSON/PERSON_ID` | PERSON_ID |
| mdm | `dams:logical/mdm/PERSON_CEO/ENTERPRISE_ID` | ENTERPRISE_ID |
| mdm | `dams:logical/mdm/PERSON_REPRESENTATIVE/ENTERPRISE_ID` | ENTERPRISE_ID |
| ucd | `dams:logical/ucd/AGREEMENT/id` | id |
| ucd | `dams:logical/ucd/AUTHORIZATION/id` | id |
| ucd | `dams:logical/ucd/EMPOYEE/id` | id |
| ucd | `dams:logical/ucd/ORGANIZATION/id` | id |
| ucd | `dams:logical/ucd/ORGANIZATION_TYPE/Id` | Id |
| ucd | `dams:logical/ucd/PERSON/id` | id |
| ucd | `dams:logical/ucd/POSITION/id` | id |

*Total identifying attribute refs: 26.*

### externally_aligned (entity-level; property TBD)

| ConceptualEntity | External target(s) | Note |
|---|---|---|
| `dams:concept/LegalEntity` | https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/LegalPerson | Candidate **entity** anchor; attributes not lifted yet |

### cross_solution (same `name` + `logical_type` in 2+ solutions)

| Name | logical_type | Solutions |
|---|---|---|
| id | identifier | crm, esed, ucd |
| inn | string | esed, mdm, ucd |
| kpp | string | esed, mdm, ucd |
| ogrn | string | esed, mdm, ucd |
| birthdate | date | crm, ucd |
| first_name | string | esed, mdm |
| full_name | string | mdm, ucd |
| last_name | string | esed, mdm |
| name | string | crm, ucd |
| snils | string | mdm, ucd |

*Total cross-solution signatures: 10.*

### critical_data

N/A — нет отдельного слота `critical_data` / regulatory flag на атрибутах; использовать `governance_classification` / policies (out of scope v1 inventory).

### regulatory

N/A — явных regulatory markers на LogicalAttribute не найдено (grep `regulatory` в связке с attrs — 0).

### governance_anchor (entity `business_importance` high/critical)

| Solution | LogicalEntity |
|---|---|
| — | *Нет записей: во всех solution YAML (`crm`/`esed`/`mdm`/`ucd`) `business_importance: medium`.* |

---

## Notes

- `definition_source_ref` доминирует по hit-count из‑за validation/remediation текстов в `*/publications/vertical_slice.json` (не model slots).
- Wave-2 soft slots (`unit_code`, `currency_attribute_ref`, `timezone_policy`, `temporal_semantics`) почти не заполнены в solution data; правила — `formal_checks.py` (ATR warnings).
- Existing transform `model-assets/transformations/dams-logical-attribute-rename-type.yaml` переименовывает `logical_type` → `attribute_type` (slice experiment); учитывать при проектировании `ConceptualProperty`.
- Hotspots для миграции: `moex-core.yaml` slot defs, `formal_checks.py`, ER projections (`dbml.py`, `mermaid_er.py`, `er_scene.py`), `standard-linkml/ingest/mapper.py`, `apps/web` `EntityForms.tsx`, `definitions.py` / ADR-025 cascade.
