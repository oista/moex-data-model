# TechnicalAsset migration: PhysicalObject inventory

Инвентаризация вхождений `PhysicalObject` / связанных слотов для миграции на `TechnicalAsset`.

**Patterns:** `PhysicalObject`, `PhysicalObjectKindEnum`, `physical_object`, `physical_objects`, `PhysicalField`, `physical_object_ref`, `physical_object_refs`, `object_kind` (когда связано с physical).

**Excluded:** `tmp/**`, `.git/**`, `**/__pycache__/**`, `**/.venv/**`, `node_modules/**`, `.cursor/plans/**`, `docs/migration/_inventory_raw.txt`.

**Source:** live `rg` (+ optional raw dump `docs/migration/_inventory_raw.txt`). Raw matches: 1829; unique files: 133; line hits: 1701.

---

## Summary: key slots / classes

| Concept | Location | Notes |
|---|---|---|
| `PhysicalObject` class | `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml:209` | `is_a: ModelElement`; mixins `HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings` |
| `PhysicalObject` slots | `moex-core.yaml:217-226` | `solution_ref`, `system_ref`, `object_kind`, `qualified_name`, `technology`, `native_schema_ref`, `direction`, `physical_fields`, `mapping_coverage_status`, `mapping_rationale` |
| `PhysicalField` class | `moex-core.yaml:228` | slots: `physical_object_ref`, `native_name`, `native_type`, `required`, `ordinal_position`, `schema_path`, `mapping_coverage_status`, `mapping_rationale` |
| `PhysicalField.physical_object_ref` | `moex-core.yaml:236` (attr), slot def `:602-603` | `range: PhysicalObject` |
| `ModelPackage.physical_objects` | `moex-core.yaml:55` (attr), slot def `:335-339` | `range: PhysicalObject`, multivalued, inlined list |
| `physical_fields` slot | `moex-core.yaml:224` (attr), slot def ~`:598` | `range: PhysicalField` |
| `object_kind` slot | `moex-core.yaml:582-583` | `range: PhysicalObjectKindEnum` |
| `PhysicalObjectKindEnum` | `moex-types.yaml:256-271` | `database`, `schema`, `table`, `view`, `column`, `api`, `endpoint`, `payload`, `topic`, `queue`, `message`, `file`, `dataset`, `pipeline` |
| `MappingTypeEnum.entity_physical` | `moex-types.yaml:301, 309-312` | description: PhysicalObject ↔ LogicalEntity |
| `DataFlowEntityBinding.physical_object_refs` | `moex-integration.yaml:47` (attr), slot def `:117-121` | `range: PhysicalObject`, `minimum_cardinality: 1` |
| `SelectedEntity.physical_object_refs` | `moex-contract-binding.yaml:51` | SelectedEntity attribute list |
| `SelectedAttribute.physical_field_refs` | `moex-contract-binding.yaml:58` | поля only; object refs нет |
| requirements `applies_target_kinds` | `moex-requirements.yaml:137` | allowlist `object_kind` / facet |

### Counts by category

| Category | Files | Line hits |
|---|---:|---:|
| 1. Schemas | 5 | 22 |
| 2. Requirements | 3 | 31 |
| 3. Examples and solution models | 24 | 787 |
| 4. Code packages | 31 | 130 |
| 5. Apps | 12 | 87 |
| 6. Tests | 22 | 75 |
| 7. Generated artifacts | 21 | 479 |
| 8. Documentation | 15 | 90 |
| **Total** | **133** | **1701** |

---

## 1. Schemas (`model-assets/specifications/moex-dams/0.1/schemas/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/schemas/moex-contract-binding.yaml` | 51 | schema | physical_object_refs |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml` | 55, 209, 219, 228, 236, 252, 335, 336, 582, 583, 598, 602, 603 | schema | PhysicalObjectKindEnum, PhysicalObject, PhysicalField, physical_objects, physical_object_ref, object_kind |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-integration.yaml` | 47, 117, 118, 123 | schema | PhysicalObject, PhysicalField, physical_object_refs |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-requirements.yaml` | 137 | schema | object_kind |
| `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml` | 256, 301, 311 | schema | PhysicalObjectKindEnum, PhysicalObject |

*Entries in section: 5 files, 22 line hits.*

## 2. Requirements (`model-assets/specifications/moex-dams/0.1/requirements/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml` | 231, 244, 248 | data | physical_objects |
| `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml` | 106, 114, 125 | data | physical_objects, physical_object_ref, object_kind |
| `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml` | 124, 126, 138, 154, 582, 594, 598, 605, 606, 608, 612, 619, 626, 633, 650, 654, 655, 657, 661, 668, 675, 693, 708, 727, 731 | data | PhysicalObject, PhysicalField, physical_object_ref, object_kind |

*Entries in section: 3 files, 31 line hits.*

## 3. Examples and solution models (`model-assets/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` | 663, 664, 750, 766, 1410, 1411, 1413, 1805, 1806, 1808, … (+19 more; last 2863) | data | PhysicalObjectKindEnum, PhysicalObject, PhysicalField, physical_objects, physical_object_refs, physical_object_ref, object_kind |
| `model-assets/implementations/imports/client-accounts-csv-draft/0.1/draft-model.yaml` | 28, 33 | data | physical_objects, object_kind |
| `model-assets/implementations/imports/client-accounts-csv-draft/0.1/publish.yaml` | 60, 65 | data | physical_objects, object_kind |
| `model-assets/implementations/solutions/crm/crm-solution-model.yaml` | 792, 800, 810, 819, 828, 837, 846, 855, 864, 873, … (+52 more; last 1351) | data | physical_objects, physical_object_ref, object_kind |
| `model-assets/implementations/solutions/crm/publications/physical.dbml` | 10, 31, 59 | document | object_kind |
| `model-assets/implementations/solutions/crm/publications/vertical_slice.json` | 460, 586, 761, 2129, 2132, 2141, 2144, 2153, 2156, 2165, … (+112 more; last 9207) | data | physical_object_ref |
| `model-assets/implementations/solutions/crm/publish.yaml` | 80, 87, 93, 96 | data | PhysicalObject, physical_objects, object_kind |
| `model-assets/implementations/solutions/esed/esed-solution-model.yaml` | 1234, 1242, 1252, 1261, 1270, 1280, 1289, 1302, 1312, 1321, … (+71 more; last 2010) | data | physical_objects, physical_object_ref, object_kind |
| `model-assets/implementations/solutions/esed/publications/physical.dbml` | 10, 19, 25, 31, 38, 67, 77, 86, 93, 99, 111, 119 | document | object_kind |
| `model-assets/implementations/solutions/esed/publications/vertical_slice.json` | 593, 635, 656, 677, 705, 887, 936, 978, 1006, 1027, … (+150 more; last 11212) | data | physical_object_ref |
| `model-assets/implementations/solutions/esed/publish.yaml` | 79, 86, 92, 95 | data | PhysicalObject, physical_objects, object_kind |
| `model-assets/implementations/solutions/mdm/mdm-solution-model.yaml` | 628, 636, 646, 655, 664, 673, 682, 691, 700, 709, … (+37 more; last 1058) | data | physical_objects, physical_object_ref, object_kind |
| `model-assets/implementations/solutions/mdm/publications/physical.dbml` | 10, 40, 56, 62 | document | object_kind |
| `model-assets/implementations/solutions/mdm/publications/vertical_slice.json` | 355, 544, 635, 656, 1621, 1624, 1633, 1636, 1645, 1648, … (+82 more; last 7039) | data | physical_object_ref |
| `model-assets/implementations/solutions/mdm/publish.yaml` | 80, 87, 93, 96 | data | PhysicalObject, physical_objects, object_kind |
| `model-assets/implementations/solutions/solution-xlsx.profile.yaml` | 77, 97, 120, 142 | data | object_kind |
| `model-assets/implementations/solutions/ucd/publications/physical.dbml` | 10, 19, 29, 42, 54, 61, 70 | document | object_kind |
| `model-assets/implementations/solutions/ucd/publications/vertical_slice.json` | 362, 404, 453, 523, 586, 614, 656, 1700, 1703, 1712, … (+82 more; last 6808) | data | physical_object_ref |
| `model-assets/implementations/solutions/ucd/publish.yaml` | 80, 87, 93, 96 | data | PhysicalObject, physical_objects, object_kind |
| `model-assets/implementations/solutions/ucd/ucd-solution-model.yaml` | 696, 704, 714, 723, 732, 741, 750, 763, 773, 782, … (+37 more; last 1140) | data | physical_objects, physical_object_ref, object_kind |
| `model-assets/specifications/moex-dams/0.1/examples/client-contract-binding.yaml` | 25 | data | physical_object_refs |
| `model-assets/specifications/moex-dams/0.1/examples/client-data-flow.yaml` | 29 | data | physical_object_refs |
| `model-assets/specifications/moex-dams/0.1/publication-requirements.yaml` | 113, 124 | data | PhysicalObject, PhysicalField |
| `model-assets/transformations/mappings/dams-fibo.sssom.yaml` | 12 | data | object_kind |

*Entries in section: 24 files, 787 line hits.*

## 4. Code packages (`packages/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `packages/drawdb-adapter/src/moex_drawdb/domain.py` | 34, 67, 68, 69 | code | object_kind |
| `packages/drawdb-adapter/src/moex_drawdb/parse.py` | 28, 56, 114 | code | object_kind |
| `packages/drawdb-adapter/src/moex_drawdb/patch.py` | 359, 366, 371, 375, 379, 416, 420, 445, 479, 518, 538, 557, 716, 718, 721, 722, 726, 728, 732, 741, 751 | code | physical_objects, physical_fields, object_kind |
| `packages/ontology-catalog/src/moex_ontology/adapters/binding_repo.py` | 46 | code | object_kind |
| `packages/ontology-catalog/src/moex_ontology/application/get_entity.py` | 50 | code | object_kind |
| `packages/ontology-catalog/src/moex_ontology/read_models/semantic_context.py` | 19 | code | object_kind |
| `packages/semantic-mappings/src/moex_semantic_mappings/sssom_adapter.py` | 34, 45 | code | object_kind |
| `packages/specification-dams/src/moex_dams/application/diff.py` | 34 | code | physical_objects |
| `packages/specification-dams/src/moex_dams/application/element_index.py` | 20, 59, 60 | code | PhysicalObject, PhysicalField, physical_objects, physical_fields |
| `packages/specification-dams/src/moex_dams/domain/graph.py` | 14, 28 | code | physical_object_ref |
| `packages/specification-dams/src/moex_dams/mappings/dams_to_graph.py` | 117, 121, 129, 208 | code | physical_objects, physical_object_ref |
| `packages/specification-dams/src/moex_dams/projection/dbml.py` | 188, 192, 197, 198 | code | PhysicalObject, physical_objects, object_kind |
| `packages/specification-dams/src/moex_dams/projection/er_scene.py` | 232, 236 | code | PhysicalObject, physical_objects |
| `packages/specification-dams/src/moex_dams/projection/mermaid_er.py` | 293, 297 | code | PhysicalObject, physical_objects |
| `packages/specification-dams/src/moex_dams/rules/cascade.py` | 66, 71 | code | PhysicalObject, PhysicalField, physical_objects, physical_fields |
| `packages/specification-dams/src/moex_dams/rules/catalog_validate.py` | 33, 34 | code | PhysicalObject, PhysicalField |
| `packages/specification-dams/src/moex_dams/rules/dams_levels.py` | 37, 74, 111 | code | physical_objects |
| `packages/specification-dams/src/moex_dams/rules/formal_checks.py` | 37, 164, 175, 210, 212, 216, 218, 229, 420, 474, 502, 519, 904, 924, 976, 1148 | code | PhysicalObject, PhysicalField, physical_objects, object_kind |
| `packages/standard-linkml/README.md` | 67, 68, 80, 81, 90 | document | PhysicalObject, PhysicalField, object_kind |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/ids.py` | 52 | code | match |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py` | 317, 321, 322, 324, 327, 329, 330, 334, 340, 343, 346, 350, 358, 369, 376, 385, 392, 434, 519, 520 | code | physical_objects, physical_object_ref, object_kind |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/profile.py` | 33, 57 | code | physical_objects, object_kind |
| `packages/standard-linkml/src/moex_standard_linkml/ingest/workbook.py` | 35, 70, 71, 85 | code | physical_objects |
| `packages/standard-linkml/src/moex_standard_linkml/provider.py` | 108 | code | physical_objects |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/build.py` | 46, 73, 78, 121, 126, 226, 227, 230 | code | PhysicalObject, PhysicalField, physical_objects, physical_fields, object_kind |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/convert.py` | 190 | code | physical_objects |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/enrich.py` | 70 | code | physical_objects |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/profile.py` | 84, 281, 282, 288, 297 | code | PhysicalObject, PhysicalField, physical_objects, object_kind |
| `packages/standard-linkml/src/moex_standard_linkml/solution_xlsx/scaffold.py` | 113, 120, 123 | code | physical_objects, object_kind |
| `packages/standard-linkml/templates/er-dictionary.profile.yaml` | 58, 59, 65, 72 | code | PhysicalObject, PhysicalField, physical_objects, object_kind |
| `packages/standard-linkml/templates/solution-xlsx.profile.yaml` | 72 | code | object_kind |

*Entries in section: 31 files, 130 line hits.*

## 5. Apps (`apps/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `apps/api/src/moex_model_api/app.py` | 139, 147 | code | match |
| `apps/api/src/moex_model_api/yaml_mutate.py` | 60, 473, 497, 501, 511, 513, 526, 542, 555, 559, 562, 566, 567, 568, 588, 603, 675, 676, 677, 678, 683, 684 | code | physical_objects, physical_object_ref, object_kind |
| `apps/viewer/src/moex_publication_viewer/models/manifest_models.py` | 57 | code | PhysicalObject |
| `apps/viewer/src/moex_publication_viewer/normalizers/helpers.py` | 95 | code | PhysicalObject, physical_fields |
| `apps/viewer/src/moex_publication_viewer/normalizers/linkml_normalizer.py` | 70 | code | PhysicalObject |
| `apps/viewer/src/moex_publication_viewer/normalizers/model_skeleton_projection.py` | 16, 17 | code | PhysicalObject, PhysicalField, physical_objects, physical_fields |
| `apps/viewer/src/moex_publication_viewer/publication_contract.py` | 28, 29, 38, 39, 253, 255, 262, 346 | code | PhysicalObject, PhysicalField, physical_objects, physical_fields |
| `apps/web/src/api/types.ts` | 194, 195, 201, 208, 215, 224 | code | object_kind |
| `apps/web/src/components/MappingForms.tsx` | 38, 50 | code | physical_objects |
| `apps/web/src/components/ModelExplorer.tsx` | 11, 138, 139, 155 | code | physical_objects |
| `apps/web/src/components/PhysicalForms.tsx` | 19, 32, 37, 46, 53, 153, 182, 211, 212, 216, 240, 246, 257, 314, 354, 458, 489, 503 | code | PhysicalObject, PhysicalField, physical_objects, object_kind |
| `apps/web/src/model/yamlMutate.ts` | 34, 121, 125, 128, 136, 138, 364, 365, 370, 377, 387, 388, 397, 407, 408, 409, 424, 432, 444, 464 | code | PhysicalObject, PhysicalField, physical_objects, physical_object_ref, object_kind |

*Entries in section: 12 files, 87 line hits.*

## 6. Tests

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `apps/api/tests/test_api.py` | 396, 401, 402, 405, 432, 455 | test | object_kind |
| `apps/api/tests/test_yaml_mutate.py` | 340, 344, 345, 349, 354, 373, 381, 383, 389, 405, 421, 429, 434 | test | physical_objects, object_kind |
| `apps/viewer/tests/test_dams_explorer_roots.py` | 199, 325, 341 | test | physical_objects |
| `apps/viewer/tests/test_dams_full_spec.py` | 32 | test | PhysicalObject |
| `apps/viewer/tests/test_hierarchy_projection.py` | 264, 318 | test | PhysicalObject, physical_objects |
| `apps/viewer/tests/test_publication_contract_phase2.py` | 39, 56, 58 | test | PhysicalObject, PhysicalField, physical_objects |
| `apps/web/src/components/ModelExplorer.test.tsx` | 21 | test | physical_objects |
| `apps/web/src/components/PhysicalForms.test.tsx` | 13, 17 | test | physical_objects, object_kind |
| `apps/web/src/components/RelationshipMappingForms.test.tsx` | 20 | test | physical_objects |
| `apps/web/src/model/yamlMutate.test.ts` | 15, 18, 39, 40, 43 | test | physical_objects, object_kind |
| `packages/drawdb-adapter/tests/test_round_trip.py` | 72, 77, 172 | test | physical_objects, object_kind |
| `packages/specification-dams/tests/test_cascade_resolver.py` | 142, 149, 161 | test | physical_objects, physical_object_ref, object_kind |
| `packages/specification-dams/tests/test_dams_levels.py` | 54 | test | physical_objects |
| `packages/specification-dams/tests/test_dbml_projection.py` | 64, 68, 82, 103, 147 | test | physical_objects, object_kind |
| `packages/specification-dams/tests/test_enterprise_conceptual.py` | 28 | test | physical_objects |
| `packages/specification-dams/tests/test_formal_checks.py` | 276, 283, 482, 488, 503, 514 | test | physical_objects, physical_fields, object_kind |
| `packages/specification-dams/tests/test_mermaid_er_projection.py` | 101, 105, 119, 140 | test | physical_objects, object_kind |
| `packages/standard-linkml/tests/fixtures/er-dictionary/PhysicalObjects.csv` | 1 | test | object_kind |
| `packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml` | 55, 56, 62, 69 | test | PhysicalObject, PhysicalField, physical_objects, object_kind |
| `packages/standard-linkml/tests/fixtures/solution-xlsx/profile.yaml` | 23, 37, 50 | test | object_kind |
| `packages/standard-linkml/tests/test_mapper.py` | 58, 59, 61, 198, 199 | test | PhysicalObject, physical_objects, object_kind |
| `packages/standard-linkml/tests/test_workbook.py` | 25, 26 | test | physical_objects |

*Entries in section: 22 files, 75 line hits.*

## 7. Generated artifacts (`generated/**`)

Сводка по типам (полный построчный dump опущен):

| Type | Files | Hits |
|---|---:|---:|
| `.ttl` | 3 | 173 |
| `.md` | 11 | 138 |
| `.py` | 2 | 75 |
| `.json` | 2 | 47 |
| `.dbml` | 2 | 44 |
| `.csv` | 1 | 2 |

### Files (path + sample lines)

| File | Line(s) | Hits | Usage |
|---|---|---:|---|
| `generated/artifacts/moex-dams/0.1/diagrams/DataFlowEntityBinding.md` | 93, 94, 98, 104, 105 | 5 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/HasGovernanceClassification.md` | 14, 15, 16, 17 | 4 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/HasOwnership.md` | 18, 19, 20, 21 | 4 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/HasPolicyBindings.md` | 14, 15, 16, 17 | 4 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/ModelElement.md` | 26, 27, 28, 29 | 4 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/ModelPackage.md` | 173, 179, 180 | 3 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/PhysicalField.md` | 6, 7, 8, 10, 12, 14, 17, 19, 21, 23, … (+37 more; last 172) (n=47) | 47 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/PhysicalObject.md` | 6, 7, 8, 10, 12, 14, 17, 19, 21, 23, … (+44 more; last 212) (n=54) | 54 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/SelectedAttribute.md` | 60, 61 | 2 | generated |
| `generated/artifacts/moex-dams/0.1/diagrams/SelectedEntity.md` | 54, 60, 61 | 3 | generated |
| `generated/artifacts/moex-dams/0.1/docs/index.md` | 49, 50, 79, 197, 207, 208, 209, 330 | 8 | generated |
| `generated/artifacts/moex-dams/0.1/entity-inventory.csv` | 15, 16 | 2 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams-drawdb-colored.dbml` | 11, 96, 458, 463, 471, 472, 474, 479, 554, 556, … (+6 more; last 718) (n=16) | 16 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams.dbml` | 246, 468, 482, 502, 514, 607, 672, 819, 866, 867, … (+18 more; last 919) (n=28) | 28 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams.owl.ttl` | 42, 196, 202, 205, 207, 208, 983, 985, 986, 1031, … (+76 more; last 4035) (n=86) | 86 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams.rdf.ttl` | 70, 71, 72, 94, 321, 371, 431, 534, 796, 797, … (+58 more; last 3273) (n=68) | 68 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams.schema.json` | 728, 2562, 2746, 3166, 3168, 3391, 3495, 3560, 3569, 3572, … (+9 more; last 4618) (n=19) | 19 | generated |
| `generated/artifacts/moex-dams/0.1/moex-dams.shacl.ttl` | 217, 447, 451, 464, 1047, 1050, 1408, 1477, 1540, 1544, … (+9 more; last 2789) (n=19) | 19 | generated |
| `generated/artifacts/moex-dams/0.1/ontology-profile.json` | 279, 281, 290, 292, 1085, 1086, 1089, 1093, 1097, 1101, … (+18 more; last 1955) (n=28) | 28 | generated |
| `generated/artifacts/moex-dams/0.1/python/moex_dams.py` | 193, 197, 1182, 1238, 1976, 1982, 1983, 1984, 1985, 1987, … (+50 more; last 4338) (n=60) | 60 | generated |
| `generated/contracts/moex-dams/0.1/src/moex_dams_contracts/__init__.py` | 434, 484, 492, 1035, 1318, 1324, 1329, 1357, 1361, 1396, 1467, 1542, 1632, 1754, 1755 | 15 | generated |

*Generated section: 21 files, 479 line hits.*

## 8. Documentation (`docs/**`)

| File | Line(s) | Usage | Keys |
|---|---|---|---|
| `docs/IMPLEMENTATION_PLAN.md` | 509, 572, 573 | document | PhysicalObject, PhysicalField |
| `docs/LinkML_Glossary_DAMS.md` | 42, 148, 175, 294 | document | object_kind |
| `docs/MOEX Data Model Specification v0.1 на основе LinkML.md` | 90, 243, 249, 494, 512, 517, 582 | document | PhysicalObject, PhysicalField, physical_objects, physical_object_refs, object_kind |
| `docs/adr/ADR-023-governed-property-cascade.md` | 57, 108 | document | PhysicalObject, PhysicalField |
| `docs/agents/er-dictionary-model-contract.md` | 33, 34, 115, 118, 126, 137, 145, 219, 295, 306 | document | PhysicalObjectKindEnum, PhysicalObject, PhysicalField, object_kind |
| `docs/agents/pdf-to-er-dictionary.md` | 26, 117, 118, 120, 122, 128, 243 | document | PhysicalObject, PhysicalField, object_kind |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | 57, 58, 298, 306, 476, 705, 735, 830, 858, 860, 875, 896, 1284 | document | PhysicalObject, PhysicalField |
| `docs/architecture/linkml_architecture.md` | 231, 368, 369 | document | PhysicalObject, PhysicalField |
| `docs/architecture/uml/01-core-data-model.puml` | 81, 84, 92, 93, 137, 138, 155, 156, 157, 172 | document | PhysicalObjectKindEnum, PhysicalObject, PhysicalField, physical_object_ref, physical_fields, object_kind |
| `docs/architecture/uml/02-solution-model-governance.puml` | 79, 81, 87, 150, 151, 183, 190, 191, 208, 225, 226 | document | PhysicalObjectKindEnum, PhysicalObject, PhysicalField, physical_objects, physical_object_refs, physical_fields, object_kind |
| `docs/architecture/uml/all_model_modules.puml` | 66, 67, 89, 90, 106, 113, 164 | document | PhysicalObject, PhysicalField, physical_objects, physical_fields |
| `docs/architecture/uml/description.md` | 17 | document | PhysicalObject, PhysicalField |
| `docs/dams_entities_list.md` | 12 | document | PhysicalObject |
| `docs/superpowers/plans/2026-09-28-pdf-to-er-dictionary-agent.md` | 15, 26 | document | PhysicalObjectKindEnum, PhysicalObject, PhysicalField |
| `docs/superpowers/specs/2026-09-28-pdf-to-er-dictionary-agent-design.md` | 22, 79, 81, 97, 99, 100, 116, 117, 124 | document | PhysicalObject, PhysicalField, object_kind |

*Entries in section: 15 files, 90 line hits.*

---

## Notes

- `object_kind` встречается и вне PhysicalObject (например SSSOM `ontology_entity` в `model-assets/transformations/mappings/dams-fibo.sssom.yaml`, ontology-catalog read-models). Оставлены в списке; при миграции не трогать, если не `PhysicalObjectKindEnum`.
- `DataFlow` не ссылается на PhysicalObject напрямую; только `DataFlowEntityBinding.physical_object_refs` и `SelectedEntity.physical_object_refs`.
- `SelectedAttribute` — только `physical_field_refs`.
- Tests под `apps/**` и `packages/**` отнесены к категории 6.
- Hotspots для PR-2/PR-3: `packages/specification-dams`, `packages/standard-linkml`, `packages/drawdb-adapter`, `apps/web` (`PhysicalForms`, `yamlMutate`), solution YAML (mdm/crm/esed/ucd), `generated/**` (регенерация).

