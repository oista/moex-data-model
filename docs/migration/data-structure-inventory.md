# DataStructure migration: PhysicalField inventory

Инвентаризация вхождений `PhysicalField` / связанных слотов для миграции на `DataStructure` / `SchemaNode` (плоский список узлов).

**Target classes (planned):** `DataStructure`, `SchemaNode` — в схемах и данных **отсутствуют** (grep `SchemaNode` ≈ 0 вне планов; `DataStructure` — только упоминания в описаниях/`HasStructure`).

**Patterns:** `PhysicalField`, `physical_fields`, `physical_field_refs`, `schema_path`, `native_type` (в контексте PhysicalField), `structure_ref`, `message_type` / `asset_kind: message_type`, `transitional`, `LogicalDataTypeEnum`, `field_mapping`, `SelectedAttribute` / `DataFlowEntityBinding` / `DataModelBinding` (field refs), `schema_dialect`, `data_format` / `HasStructure`, `PDM-002`, `PDM-004`, `PDM-009`.

**Excluded:** `tmp/**`, `.git/**`, `**/__pycache__/**`, `**/.venv/**`, `node_modules/**`, `.cursor/plans/**`.

**Source:** live scan via `docs/migration/_build_data_structure_inventory.py` (+ raw dump `docs/migration/_ds_inventory_raw.txt`). Core pattern line hits: 2165; unique files: 317 (incl. generated/bundles mirrors and tooling `schema_path` noise — see Notes).

---

## Summary: key slots / classes

| Concept | Location | Notes |
|---|---|---|
| `PhysicalField` class | `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml:284-301` | `is_a: ModelElement`; mixins ownership/governance/policy; slots `carrier_ref`, `native_name`, `native_type`, `required`, `ordinal_position`, `schema_path`, mapping coverage |
| `physical_fields` slot | `moex-core.yaml:728-732`; attr on `DataCarrier` `moex-technical.yaml:107` | `range: PhysicalField`, multivalued, inlined list |
| `carrier_ref` | `moex-core.yaml:294`, slot def `:452` | Parent DataCarrier (replaces legacy `physical_object_ref`) |
| `schema_path` (PhysicalField) | `moex-core.yaml:299`, slot def `:742-743` | Optional string path within carrier schema |
| `native_type` (PhysicalField) | `moex-core.yaml:296`, slot def `:736-738` | Required string; **distinct** from `NativeTypeBinding.dialect_native_type` (`moex-datatypes.yaml:242`) |
| `HasStructure` mixin | `moex-technical.yaml:18-26` | On `DataCarrier`: `structure_ref`, `schema_dialect`, `data_format` |
| `structure_ref` | `moex-technical.yaml:222-225` | Temporary uriorcurie; planned → `DataStructure` |
| `schema_dialect` | `moex-technical.yaml:226-228` | **No instance values** in model-assets (schema def + hierarchy mirror only) |
| `data_format` | `moex-technical.yaml:229-231` | No values in solution YAML |
| `DataCarrierKindEnum.message_type` | `moex-technical.yaml:279-280` | Transitional; enum exists, **no solution carriers use it** |
| `MappingTypeEnum.field_mapping` | `moex-types.yaml:286-297` | PhysicalField ↔ LogicalAttribute |
| `SelectedAttribute.physical_field_refs` | `moex-contract-binding.yaml:54-59` | Fields only |
| `DataFlowEntityBinding.physical_field_refs` | `moex-integration.yaml:49`, slot `:124-125` | `range: PhysicalField` |
| `DataModelBinding` | `moex-contract-binding.yaml:20+` | Package binding; field refs via nested `SelectedAttribute` |
| `PDM-002` / `PDM-004` / `PDM-009` | `it-solution-requirements.yaml:646+`, `:721+`, `:828+` | Field core slots; field↔attribute mapping; Mapping endpoint types |
| `LogicalDataTypeEnum` | `moex-types.yaml:243-255` | **Seed catalogue only** (ADR-036); `LogicalAttribute` uses `data_type_ref` |

### PhysicalField instance counts (inlined under `physical_fields`)

| Source | Count |
|---|---:|
| `mdm/mdm-solution-model.yaml` | **42** |
| `crm/crm-solution-model.yaml` | 58 |
| `esed/esed-solution-model.yaml` | 68 |
| `ucd/ucd-solution-model.yaml` | 39 |
| **Solutions subtotal** | **207** |
| `imports/.../draft-model.yaml` | 2 |
| **Solutions + draft (plan ≈209)** | **209** |
| `requirements/examples/it-solution-model.example.yaml` | 1 |
| **All model-assets data instances** | **210** |

### Counts by inventory category (core pattern line hits)

| Category | Files | Line hits |
|---|---:|---:|
| 1. Schemas | 6 | 24 |
| 2. Requirements | 3 | 41 |
| 3. Examples and solution models | 8 | 332 |
| 4. Code packages | 40 | 196 |
| 5. Apps | 27 | 94 |
| 6. Tests | 30 | 91 |
| 7. Generated artifacts | 168 | 1218 |
| 8. Documentation | 25 | 135 |
| 9. Other (scripts/tools) | 10 | 34 |
| **Total** | **317** | **2165** |

*Package hotspots (subset of cat. 4):* `specification-dams` 18 files / 83 hits; `standard-linkml` 14 / 78; `drawdb-adapter` 1 / 14; `publication` 2 / 3.

---

## Explicit findings (migration blockers / non-blockers)

### `schema_dialect` — no instance values

| Finding | Detail |
|---|---|
| Schema definition | `moex-technical.yaml:25`, `:226-228` (`HasStructure`) |
| Hierarchy mirror | `moex-dams-full.yaml` — slot/class mirror meta only (`schema_dialect:` as slot name, not carrier value) |
| Solution / draft / example YAML | **0** filled `schema_dialect:` values |
| Migration | Value migration **not needed**; still deprecate slot in PR-1 |

### `message_type` — enum only; unused on carriers

| Finding | Detail |
|---|---|
| Enum | `DataCarrierKindEnum.message_type` (`moex-technical.yaml:279-280`), description: transitional → Message/DataStructure |
| KIND_MAP | `payload` / `message` → `message_type` (`packages/standard-linkml/.../ingest/technical_asset.py:20-26`) |
| `TRANSITIONAL_KINDS` | `{"payload", "message", "message_type"}` → annotation `transitional: "true"` on ingest (`mapper.py:483-484`) |
| Solution carriers (mdm/crm/esed/ucd) | **0** `asset_kind: message_type` |

### `LogicalDataTypeEnum` — seed only

| Finding | Detail |
|---|---|
| Enum still defined | `moex-types.yaml:243-255` |
| LogicalAttribute | Uses `data_type_ref` / `value_domain_ref` (`moex-core.yaml:196-220`); **not** `logical_type` → enum |
| ADR-036 | Enum retained as starter DataType name catalogue; not the runtime type of attributes |
| Solution data | Attributes use `data_type_ref: dams:datatype/...` |

### Bindings referencing fields

| Class | Field slot | Notes |
|---|---|---|
| `SelectedAttribute` | `physical_field_refs` | Contract selection → PhysicalField |
| `DataFlowEntityBinding` | `physical_field_refs` | Flow binding → PhysicalField |
| `DataModelBinding` | via `SelectedAttribute` | No direct field slot on binding root |
| `Mapping` (`field_mapping`) | `source_refs` / `target_refs` | Endpoints LogicalAttribute ↔ PhysicalField (PDM-009) |

---

## 1. Schemas (`model-assets/specifications/moex-dams/0.1/schemas/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `moex-contract-binding.yaml` | 59 | schema | physical_field_refs |
| `moex-core.yaml` | 284, 299, 310, 311, 728, 729, 742 | schema | PhysicalField, field_mapping, physical_fields, schema_path |
| `moex-datatypes.yaml` | 242 | schema | PhysicalField, native_type (contrast note) |
| `moex-integration.yaml` | 49, 124, 125 | schema | PhysicalField, physical_field_refs |
| `moex-technical.yaml` | 18, 21, 24, 25, 100, 107, 177, 222, 226 | schema | HasStructure, structure_ref, schema_dialect, data_format, physical_fields |
| `moex-types.yaml` | 286, 296, 297 | schema | PhysicalField, field_mapping |

*Entries in section: 6 files, 24 line hits.*

---

## 2. Requirements (`.../requirements/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `requirements/README.md` | 41 | document | field_mapping |
| `requirements/examples/it-solution-model.example.yaml` | 121, 135, 147 | data | field_mapping, physical_fields, structure_ref |
| `requirements/it-solution-requirements.yaml` | 506, 592, 628+, 646–687 (PDM-002), 721–743 (PDM-004), 828–848 (PDM-009), … | data | PDM-002, PDM-004, PDM-009, PhysicalField, field_mapping, structure_ref |

### PDM requirements tied to PhysicalField

| Code | Name | Applies | Enforced by |
|---|---|---|---|
| PDM-002 | physical_field_core | `PhysicalField` | slot_required: `carrier_ref`, `native_name`, `native_type`, `required` |
| PDM-004 | field_attribute_mapping | `PhysicalField` | `pdm004_field_mapping` / `field_mapping` or exception |
| PDM-009 | mapping_endpoint_types | `Mapping` | `check_mapping_endpoint_types` (`technical_assets.py`) — `field_mapping` ends = LogicalAttribute ↔ PhysicalField |

*Entries in section: 3 files, 41 line hits.*

---

## 3. Examples and solution models (`model-assets/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 902+, … (n=67) | meta dump | HasStructure, PhysicalField, schema_dialect, physical_fields, … |
| `implementations/imports/client-accounts-csv-draft/0.1/draft-model.yaml` | 32, 44 | data | physical_fields (2), field_mapping |
| `implementations/solutions/crm/crm-solution-model.yaml` | 801+, … (n=64) | data | physical_fields (58), field_mapping, structure_ref |
| `implementations/solutions/esed/esed-solution-model.yaml` | 1244+, … (n=92) | data | physical_fields (68), field_mapping, structure_ref |
| `implementations/solutions/mdm/mdm-solution-model.yaml` | 639+, … (n=50) | data | physical_fields (**42**), field_mapping, structure_ref |
| `implementations/solutions/ucd/ucd-solution-model.yaml` | 705+, … (n=54) | data | physical_fields (39), field_mapping, structure_ref |
| `specifications/.../examples/client-contract-binding.yaml` | 31 | data | physical_field_refs |
| `specifications/.../publication-requirements.yaml` | 124, 136 | data | PhysicalField, field_mapping |

`structure_ref` on carriers is populated (oracle:/dynamics:/postgres:/esed: URIs). `schema_dialect` / `data_format` are **not**.

*Entries in section: 8 files, 332 line hits.*

---

## 4. Code packages (`packages/**`)

### specification-dams

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `.../application/diff.py` | 31, 79, 86, 90 | code | physical_fields, schema_path |
| `.../application/element_index.py` | 62, 63 | code | PhysicalField, physical_fields |
| `.../mappings/dams_to_graph.py` | 98, 232 | code | physical_fields |
| `.../projection/dbml.py` | 216, 268, 280 | code | physical_fields, field_mapping |
| `.../projection/er_scene.py` | 86, 242, 292 | code | physical_fields, field_mapping |
| `.../projection/mermaid_er.py` | 196, 200, 303, 359 | code | physical_fields, field_mapping |
| `.../rules/cascade.py` | 66, 74 | code | PhysicalField, physical_fields |
| `.../rules/catalog_validate.py` | 38 | code | PhysicalField |
| `.../rules/formal_checks.py` | 172+, 868+, … (n=15) | code | PhysicalField, physical_fields, field_mapping, structure_ref |
| `.../rules/technical_assets.py` | 246+, 290–318 | code | PDM-009, PhysicalField, physical_fields, field_mapping |

### standard-linkml

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `.../ingest/mapper.py` | 380, 481–545, 580, … (n=17) | ingest | physical_fields, structure_ref, native_type, schema_path, field_mapping |
| `.../ingest/technical_asset.py` | (KIND_MAP / TRANSITIONAL_KINDS) | ingest | message_type, transitional |
| `.../ingest/workbook.py` | 36, 73, 74, 86 | ingest | physical_fields |
| `.../ingest/profile.py` | 41, 47, 64 | ingest | physical_fields, structure_ref |
| `.../solution_xlsx/build.py` | 47, 145, 170, 235, 236 | code | PhysicalField, physical_fields, field_mapping |
| `.../solution_xlsx/profile.py` | 320, 321 | code | PhysicalField, physical_fields |
| `templates/er-dictionary.profile.yaml` | 70–72, 81 | profile | PhysicalField, physical_fields, structure_ref |
| `README.md` | 68, 80–82, 90 | document | PhysicalField, field_mapping |

### drawdb-adapter / publication

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `drawdb-adapter/.../patch.py` | 433+, … (n=14) | code | physical_fields, field_mapping |
| `publication/.../build_publication.py` | 267, 274 | code | schema_path* |
| `publication/.../cli.py` | 31 | code | schema_path* |

\*Many package/app `schema_path` hits are **LinkML SchemaView file paths**, not `PhysicalField.schema_path`. Filter by class/slot context when migrating.

*Entries in section: 40 files, 196 line hits (incl. cache/egg-info noise).*

---

## 5. Apps (`apps/**`)

| Area | Files (sample) | Usage | Keys |
|---|---|---|---|
| API mutate | `apps/api/.../yaml_mutate.py` | CRUD carriers/fields | physical_fields, structure_ref |
| Web forms | `PhysicalForms.tsx`, `MappingForms.tsx`, `yamlMutate.ts` | UI | PhysicalField, physical_fields, field_mapping |
| Viewer | `publication_contract.py`, `model_skeleton_projection.py`, `helpers.py` | contract / skeleton | PhysicalField, physical_fields |
| CLI | `import_.py`, `bootstrap.py`, … | mostly schema_path* | tooling paths |

*Entries in section: 27 files, 94 line hits (incl. `viewer/dist` mirrors).*

---

## 6. Tests

| Area | Sample | Keys |
|---|---|---|
| specification-dams | `test_formal_checks.py` (PDM-002/004), `test_technical_asset_checks.py` (PDM-009), projections | physical_fields, field_mapping, PDM-* |
| standard-linkml | `test_mapper.py`, fixtures `PhysicalFields.csv`, `er-dictionary/profile.yaml` | physical_fields, structure_ref |
| drawdb-adapter | `test_round_trip.py` | physical_fields, field_mapping |
| apps api/web/viewer | `test_yaml_mutate.py`, `PhysicalForms.test.tsx`, `test_publication_contract_phase2.py` | physical_fields |
| migration | `tests/migration/test_migrate_physical_to_technical_asset.py` | physical_fields, structure_ref |

*Entries in section: 30 files, 91 line hits.*

---

## 7. Generated artifacts (`generated/**`)

Сводка по типам (полный построчный dump в `_ds_inventory_raw.txt`; bundles mirror artifacts):

| Type | Files | Hits |
|---|---:|---:|
| `.md` | 134 | 752 |
| `.json` | 20 | 88 |
| `.ttl` | 6 | 180 |
| `.py` | 4 | 154 |
| `.dbml` | 3 | 43 |
| `.csv` | 1 | 1 |

### Key non-bundle files

| File | Hits | Notes |
|---|---:|---|
| `.../diagrams/PhysicalField.md` | 46 | class diagram |
| `.../docs/PhysicalField.md` | 97 | generated docs |
| `.../docs/HasStructure.md` / `schema_dialect.md` / `structure_ref.md` | ~8–29 | HasStructure surface |
| `.../python/moex_dams.py` | 57 | generated Python |
| `.../moex-dams.{owl,rdf,shacl}.ttl` / `.schema.json` | 19–38 | regenerate on schema change |
| `generated/contracts/.../__init__.py` | (contracts) | Pydantic/enums |

*Generated section: 168 files, 1218 line hits (≈½ are `generated/bundles/**` duplicates).*

---

## 8. Documentation (`docs/**`)

| File / area | Relevance |
|---|---|
| `docs/adr/ADR-033-technical-asset-quantum-boundary.md` | Fields are not TechnicalAsset quanta |
| `docs/adr/ADR-036-datatype-system.md` | LogicalDataTypeEnum seed catalogue |
| `docs/architecture/uml/01-core-data-model.puml`, `02-...`, `all_model_modules.puml` | PhysicalField / HasStructure UML |
| `docs/agents/er-dictionary-model-contract.md`, `pdf-to-er-dictionary.md` | ER ingest → PhysicalField |
| `docs/migration/technical-asset-inventory.md` | Prior PhysicalObject → TechnicalAsset inventory |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | PDM / PhysicalField narrative |

*Entries in section: 25 files, 135 line hits.*

---

## ER ingest: how PhysicalField is created

**File:** `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py`

1. **Carrier prep** (~479–487): for DataCarrier collections, set optional `structure_ref` from `native_schema_ref`, init `physical_fields: []`; if kind ∈ `TRANSITIONAL_KINDS` (`payload` / `message` / `message_type`), set `annotations.transitional = "true"`.
2. **Field loop** (~489–546): for each row in workbook sheet `physical_fields`:
   - resolve owner carrier by `object` name;
   - require `name`, `native_type`;
   - build dict: `element_id` (via `ids.physical_field_id`), `carrier_ref`, `native_name`, `native_type`, `required`, optional `schema_path`;
   - `owner["physical_fields"].append(pf)`;
   - register `field_by_dotted["{object}.{name}"]` for Mapping resolution.
3. **Mappings** (~548+): `field_mapping` rows resolve dotted field ids via `field_by_dotted`.

Related: sheet load in `ingest/workbook.py`; kind map in `ingest/technical_asset.py` (`KIND_MAP`, `TRANSITIONAL_KINDS`).

---

## Notes

- **`schema_path` ambiguity:** PhysicalField slot vs LinkML tooling parameter (`SchemaView(schema_path=...)`, CLI flags). Migration of the *slot* is carrier/field-scoped; do not rewrite tooling call sites as Structure migration.
- **`native_type`:** on PhysicalField (string) vs `NativeTypeBinding` / datatypes module — keep separate when introducing SchemaNode type refs to `DataType` / `NativeTypeBinding`.
- **`structure_ref`:** already used as opaque URIs on carriers; PR-2 replaces with real `DataStructure` ids / `structure_ref` semantics per ADR-038+.
- **Hotspots for PR-1/PR-2:** `moex-core.yaml` PhysicalField, `moex-technical.yaml` HasStructure/`message_type`, `formal_checks.py` + `technical_assets.py` (PDM-002/004/009), `standard-linkml/ingest/mapper.py`, `drawdb-adapter/patch.py`, `apps/web` PhysicalForms/yamlMutate, solution YAML (mdm first), `generated/**` regenerate.
- Tests under `apps/**` and `packages/**` are category 6; scripts under `scripts/` / `tools/` are category 9.
