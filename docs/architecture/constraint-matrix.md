---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Constraint matrix (ADR-045)

Автогенерируется `scripts/check_constraint_matrix.py`. Источник: `model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml`. Не редактировать вручную.

**matrix_id:** `dams:constraint-matrix/0.1`  
**registry size:** 53  
**invariants:** 53

| ID | Title | Levels | Status | L1 | L2 | L3 | Source status | Scope | Source |
|---|---|---|---|---|---|---|---|---|---|
| INV-001 | ConceptualProperty identifying → is_identifying | L1, L2, L3 | implemented | waived | implemented | implemented | aligned | moex-dams | ADR-034:58; slot is_identifying |
| INV-002 | DataType.precision только для decimal | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | slot precision; ADR-036 |
| INV-003 | DataType.scale только для decimal | L1, L3 | implemented | implemented | not-applicable | implemented | partial | moex-dams | slot scale |
| INV-004 | DataType.max_length только для string/binary | L1, L3 | implemented | implemented | not-applicable | implemented | partial | moex-dams | slot max_length |
| INV-005 | DataType.min_length только для string/binary | L1, L3 | implemented | implemented | not-applicable | implemented | partial | moex-dams | slot min_length |
| INV-006 | ValueDomain enumerated → permissible_values | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | ADR-035:28; slot value_domain_kind |
| INV-007 | ValueDomain described без permissible_values | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | ADR-035:28 |
| INV-008 | ValueDomain reference_set без permissible_values | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | ADR-035:28 |
| INV-009 | ConceptualDomain described без value_meanings | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | ADR-035 |
| INV-010 | DataStructure source_pointer → source_artifact_ref | L1, L2, L3 | implemented | implemented | implemented | implemented | partial | moex-dams | slot source_pointer; ADR-038 |
| INV-011 | DataStructure schema_dialect только JSON Schema family | L1, L2, L3 | implemented | implemented | implemented | implemented | aligned | moex-dams | ADR-038:44-51 |
| INV-012 | SchemaNode array\|map → item_node, без children | L1, L2, L3 | implemented | implemented | implemented | implemented | aligned | moex-dams | ADR-038:31; PDM-020 |
| INV-013 | SchemaNode scalar\|enum без children и item_node | L1, L2, L3 | implemented | waived | implemented | implemented | aligned | moex-dams | PDM-020 |
| INV-014 | SchemaNode reference → reference_target | L1, L2, L3 | implemented | implemented | implemented | implemented | partial | moex-dams | ADR-038:32; slot reference_target |
| INV-015 | DataCarrier in_memory без location_uri и region | L1, L2, L3 | implemented | waived | implemented | implemented | aligned | moex-dams | PDM-012 |
| INV-016 | AccessPoint operation → interface_ref | L1, L2, L3 | implemented | implemented | implemented | implemented | aligned | moex-dams | PDM-011; slot interface_ref |
| INV-017 | AccessPoint interface без operation-полей | L1, L2, L3 | implemented | waived | implemented | implemented | partial | moex-dams | ADR-040:40-41; PDM-018 |
| INV-018 | direction запрещён для DataContainer и ExecutionAsset | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | moex-technical.yaml; PDM-008 |
| INV-019 | message_refs только у operation/channel | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | moex-structure.yaml; ADR-040:40-41; PDM-018 |
| INV-020 | SchemaNode без циклов children/item_node | L2, L3 | implemented | not-applicable | implemented | waived | aligned | moex-dams | ADR-038:32; PDM-014 |
| INV-021 | Реляционные признаки только при relational | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-038:40-42; PDM-016 |
| INV-022 | local_key уникален в DataStructure | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-038; PDM-013 |
| INV-023 | dams_model_level согласован с профилем | L2 | waived | not-applicable | waived | not-applicable | partial | moex-dams | ADR-021:32; moex-core.yaml |
| INV-024 | scope_ref system ∈ member_system_refs | L2 | waived | not-applicable | waived | not-applicable | partial | moex-dams | moex-governance.yaml; ADR-025:112 |
| INV-025 | tags только из реестра переходных тегов | L2 | waived | not-applicable | waived | not-applicable | aligned | moex-dams | ADR-043:28,35 |
| INV-026 | URI префикса оканчивается на / или # | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-030:40 |
| INV-027 | Владелец пакета и классификация сущности | L2 | waived | not-applicable | waived | not-applicable | partial | moex-dams | ADR-023:73-74 |
| INV-028 | RealizesMapping.mapping_type = realizes | L1, L3 | implemented | implemented | not-applicable | implemented | aligned | moex-dams | moex-core.yaml RealizesMapping rule 0; ADR-046 |
| INV-029 | EntityPhysicalMapping.mapping_type = entity_physical | L1 | implemented | implemented | not-applicable | not-applicable | aligned | moex-dams | moex-core.yaml EntityPhysicalMapping rule 0; ADR-046 |
| INV-030 | EntityPhysicalMapping.mapping_cardinality = one_to_one | L1 | implemented | implemented | not-applicable | not-applicable | aligned | moex-dams | moex-core.yaml EntityPhysicalMapping rule 1; ADR-046 |
| INV-031 | FieldMapping.mapping_type = field_mapping | L1 | implemented | implemented | not-applicable | not-applicable | aligned | moex-dams | moex-core.yaml FieldMapping rule 0; ADR-046 |
| INV-032 | AlignsWithMapping.mapping_type = aligns_with | L1 | implemented | implemented | not-applicable | not-applicable | aligned | moex-dams | moex-core.yaml AlignsWithMapping rule 0; ADR-046 |
| INV-033 | EntityPhysicalMapping endpoints DataCarrier→LogicalEntity | L2, L3 | implemented | not-applicable | implemented | implemented | aligned | moex-dams | PDM-009.c1; ADR-046 |
| INV-034 | FieldMapping endpoints LogicalAttribute→SchemaNodeRef | L2, L3 | implemented | not-applicable | implemented | implemented | aligned | moex-dams | PDM-009.c2/c3; ADR-046; ADR-039 |
| INV-035 | RealizesMapping endpoints Logical→Conceptual | L2, L3 | implemented | not-applicable | implemented | implemented | aligned | moex-dams | PDM-009; ADR-046; ADR-029 |
| INV-036 | AlignsWithMapping ConceptualEntity→http(s) IRI | L2, L3 | implemented | not-applicable | implemented | implemented | aligned | moex-dams | PDM-009; ADR-046 |
| INV-037 | FieldMapping.target_refs SchemaNodeRef pattern | L3 | implemented | not-applicable | not-applicable | implemented | aligned | moex-dams | moex-types.yaml SchemaNodeRef; ADR-046; ADR-039 |
| INV-038 | DataFlow.integration_ref resolvable in catalog snapshot | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-048; DAMS-F-007; FLW-002 |
| INV-039 | DataFlowEntityBinding.catalog_operation_ref in snapshot | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-048; FLW-003 |
| INV-040 | DataFlow.bound_catalog_revision matches snapshot | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-048; FLW-004 |
| INV-041 | DataModelBinding.catalog_revision matches snapshot | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-048; FLW-005 |
| INV-042 | solution scope requires solution and conceptual refs | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-021; dams_levels; audit solution package without solution |
| INV-043 | genesis_kind consistent with external_class_refs | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-026; audit genesis native with alignments |
| INV-044 | inverse_label required when RelationTerm not symmetric | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-026; audit inverse label vs symmetric |
| INV-045 | LogicalAttribute max cardinality >= min | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit min/max cardinality; LogicalAttribute slots |
| INV-046 | ConceptualEntity parent_concept_ref acyclic | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit cyclic inheritance/containment |
| INV-047 | TechnicalAsset parent_ref acyclic | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | PDM-006; audit cyclic containment |
| INV-048 | selected attributes belong to selected entity | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit selection field outside selected object |
| INV-049 | compatibility_mode requires baseline when not none | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit incompatible baseline/mode combos |
| INV-050 | element_id unique within package document | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit duplicate ids |
| INV-051 | mapping_cardinality matches endpoint counts | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-046; audit mapping cardinality |
| INV-052 | LogicalAttribute.owner_entity_ref equals containing entity | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | ADR-050; audit containment consistency |
| INV-053 | Relationship ends are conceptual or logical entities | L2 | implemented | not-applicable | implemented | not-applicable | aligned | moex-dams | audit Relation model; untyped uriorcurie ends |

## Statements

### INV-001: ConceptualProperty identifying → is_identifying

Если property_kind = identifying, то is_identifying должен быть задан как true.

*Notes:* L1 waived (boolean equals_string defect). L2 DAMS-INV-001 + fixtures; L3 — PR-C4b.

*adr_ref:* `ADR-045`

### INV-002: DataType.precision только для decimal

Слот precision допустим только при type_family = decimal.

### INV-003: DataType.scale только для decimal

Слот scale допустим только при type_family = decimal.

### INV-004: DataType.max_length только для string/binary

Слот max_length допустим только при type_family string или binary.

### INV-005: DataType.min_length только для string/binary

Слот min_length допустим только при type_family string или binary.

### INV-006: ValueDomain enumerated → permissible_values

Для value_domain_kind = enumerated обязательны permissible_values.

### INV-007: ValueDomain described без permissible_values

Для value_domain_kind = described слот permissible_values отсутствует.

### INV-008: ValueDomain reference_set без permissible_values

Для value_domain_kind = reference_set слот permissible_values отсутствует.

### INV-009: ConceptualDomain described без value_meanings

Для conceptual_domain_kind = described слот value_meanings отсутствует.

### INV-010: DataStructure source_pointer → source_artifact_ref

Наличие source_pointer требует source_artifact_ref.

*Notes:* PR-C3: L2 привязан к тексту слота (указатель внутри source_artifact_ref), без расширения нормы. Unit-тесты test_invariant_l2.py.

### INV-011: DataStructure schema_dialect только JSON Schema family

schema_dialect допустим только при schema_format json_schema, openapi_schema или other (other — AsyncAPI Multi Format Schema и прочие диалекты).

*Notes:* PR-C4a: schema_format other allowed with schema_dialect (AsyncAPI Multi Format Schema / ADR-038). L1+L2 widened together.

### INV-012: SchemaNode array|map → item_node, без children

Для node_kind array или map обязателен item_node и запрещены children.

*requirement_refs:* `DAMS-REQ-PDM-020.c1`, `DAMS-REQ-PDM-020.c2`

### INV-013: SchemaNode scalar|enum без children и item_node

Для node_kind scalar или enum запрещены children и item_node.

*Notes:* L1 multi-ABSENT ослаблен в JSON Schema (linkml-rules-support §3.2).

*requirement_refs:* `DAMS-REQ-PDM-020.c3`, `DAMS-REQ-PDM-020.c4`

*adr_ref:* `ADR-045`

### INV-014: SchemaNode reference → reference_target

Для node_kind = reference обязателен reference_target.

*Notes:* PR-C3: L2 привязан к тексту слота reference_target; unit-тесты test_invariant_l2.py.

### INV-015: DataCarrier in_memory без location_uri и region

Для asset_kind = in_memory запрещены location_uri и region.

*Notes:* L1 multi-ABSENT ослаблен в JSON Schema (linkml-rules-support §3.2).

*requirement_refs:* `DAMS-REQ-PDM-012.c1`

*adr_ref:* `ADR-045`

### INV-016: AccessPoint operation → interface_ref

Для access_point_kind = operation обязателен interface_ref.

*requirement_refs:* `DAMS-REQ-PDM-011.c1`

### INV-017: AccessPoint interface без operation-полей

Для access_point_kind = interface запрещены operation_name, http_method, path_template, message_refs.

*Notes:* ADR явно называет только message_refs; L1 multi-ABSENT ослаблен.

*requirement_refs:* `DAMS-REQ-PDM-018.c1`

*adr_ref:* `ADR-045`

### INV-018: direction запрещён для DataContainer и ExecutionAsset

Слот direction не задаётся у DataContainer и ExecutionAsset.

*Notes:* L1 rules в схеме нет (описание устарело). PR-C3: L2 check_direction_forbidden с invariant_id=INV-018; unit-тест test_inv_018_direction_forbidden_tagged.

*requirement_refs:* `DAMS-REQ-PDM-008.c1`

### INV-019: message_refs только у operation/channel

message_refs допустимы только у AccessPoint kind operation или channel.

*Notes:* L1 частично покрыт INV-017 (только interface). PR-C3: tagged INV-019.

*requirement_refs:* `DAMS-REQ-PDM-018.c2`

### INV-020: SchemaNode без циклов children/item_node

Рёбра children и item_node не образуют циклов.

*Notes:* PR-C3 tagged INV-020 on existing cycle checker; L3 — PR-C4.

*requirement_refs:* `DAMS-REQ-PDM-014.c1`

*adr_ref:* `ADR-045`

### INV-021: Реляционные признаки только при relational

Реляционные признаки узла допустимы только при schema_format = relational.

*Notes:* PR-C3 tagged INV-021 on existing relational-slot checker.

*requirement_refs:* `DAMS-REQ-PDM-016.c1`

### INV-022: local_key уникален в DataStructure

local_key уникален внутри одной DataStructure.

*Notes:* PR-C3 tagged INV-022 on existing uniqueness checker.

*requirement_refs:* `DAMS-REQ-PDM-013.c1`

### INV-023: dams_model_level согласован с профилем

dams_model_level допустим только для профиля dams-data-model; согласован с implementation_scope.

*Notes:* PR-C3: source_status=partial — валидатор не добавлялся без подтверждённой нормы; dams_levels уже есть, привязка INV отложена.

*adr_ref:* `ADR-045`

### INV-024: scope_ref system ∈ member_system_refs

При scope_kind = system значение scope_ref входит в ITSolution.member_system_refs.

*Notes:* PR-C3: источник partial — валидатор не изобретался.

*adr_ref:* `ADR-045`

### INV-025: tags только из реестра переходных тегов

Значения tags принадлежат реестру переходных тегов (ADR-043).

*Notes:* PR-C3: instance-валидатор tags в moex_dams/rules не найден (residue architecture-check); остаётся planned.

*adr_ref:* `ADR-045`

### INV-026: URI префикса оканчивается на / или #

URI префикса онтологии оканчивается на '/' или '#'.

*Notes:* PR-C3: tagged MOEX-ONT-004 с invariant_id=INV-026 (schema lint, не package).

### INV-027: Владелец пакета и классификация сущности

У пакета задан data_owner_ref; у логической сущности есть эффективная классификация.

*Notes:* PR-C3: source_status=partial — каскад не оформлялся как новый INV-валидатор.

*adr_ref:* `ADR-045`

### INV-028: RealizesMapping.mapping_type = realizes

У RealizesMapping слот mapping_type равен realizes.

*Notes:* L3 SPARQL mirrors LinkML PRESENT precondition (fail only when present and wrong).

*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-029: EntityPhysicalMapping.mapping_type = entity_physical

У EntityPhysicalMapping слот mapping_type равен entity_physical.

*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-030: EntityPhysicalMapping.mapping_cardinality = one_to_one

У EntityPhysicalMapping слот mapping_cardinality равен one_to_one.

*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-031: FieldMapping.mapping_type = field_mapping

У FieldMapping слот mapping_type равен field_mapping.

*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-032: AlignsWithMapping.mapping_type = aligns_with

У AlignsWithMapping слот mapping_type равен aligns_with.

*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-033: EntityPhysicalMapping endpoints DataCarrier→LogicalEntity

EntityPhysicalMapping.source_refs ⊆ DataCarrier (ровно 1) и target_refs ⊆ LogicalEntity (ровно 1); направление carrier→logical.


*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-034: FieldMapping endpoints LogicalAttribute→SchemaNodeRef

FieldMapping.source_refs ⊆ LogicalAttribute; target_refs соответствуют pattern dams:structure/…#… и резолвятся в data_structures.nodes.


*Notes:* L2 checks kinds+pattern+resolve; L3 here is endpoint minCount. SchemaNodeRef pattern alone is INV-037 (gen-shacl missed typeof pattern).


*requirement_refs:* `DAMS-REQ-PDM-009.c2`

*adr_ref:* `ADR-046`

### INV-035: RealizesMapping endpoints Logical→Conceptual

RealizesMapping.source_refs ⊆ LogicalEntity|ConceptualEntity (min 1); target_refs ⊆ ConceptualEntity (min 1; внешние conceptual id допустимы).


*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-036: AlignsWithMapping ConceptualEntity→http(s) IRI

AlignsWithMapping.source_refs — ровно один ConceptualEntity; target_refs — абсолютные http(s) IRI.


*requirement_refs:* `DAMS-REQ-PDM-009.c1`

*adr_ref:* `ADR-046`

### INV-037: FieldMapping.target_refs SchemaNodeRef pattern

У FieldMapping каждый target_refs соответствует pattern SchemaNodeRef (^dams:structure/.+#.+$). L1 — typeof SchemaNodeRef; L3 — manual SHACL (gen-shacl не эмитит pattern на слот).


*Notes:* L1 covered by SchemaNodeRef typeof pattern in JSON Schema; L2 pattern check is part of INV-034 / check_mapping_endpoint_types.


*requirement_refs:* `DAMS-REQ-PDM-009.c2`

*adr_ref:* `ADR-046`

### INV-038: DataFlow.integration_ref resolvable in catalog snapshot

DataFlow.integration_ref must parse as {catalog}:{kind}/{external_id} and resolve to an object in the file catalog snapshot. Unknown catalog prefix or missing object is an error (orphan_ref / unknown_catalog).


*requirement_refs:* `DAMS-REQ-FLW-002.c1`

*adr_ref:* `ADR-048`

### INV-039: DataFlowEntityBinding.catalog_operation_ref in snapshot

If DataFlowEntityBinding.catalog_operation_ref is set, it must identify an operation on the resolved integration object in the catalog snapshot.


*requirement_refs:* `DAMS-REQ-FLW-003.c1`

*adr_ref:* `ADR-048`

### INV-040: DataFlow.bound_catalog_revision matches snapshot

When DataFlow.bound_catalog_revision is set, it must equal the catalog_revision of the file catalog snapshot (else stale_revision warning).


*requirement_refs:* `DAMS-REQ-FLW-004.c1`

*adr_ref:* `ADR-048`

### INV-041: DataModelBinding.catalog_revision matches snapshot

When DataModelBinding.catalog_revision is set, it must equal the catalog_revision of the file catalog snapshot (topology change without contract rebuild).


*requirement_refs:* `DAMS-REQ-FLW-005.c1`

*adr_ref:* `ADR-048`

### INV-042: solution scope requires solution and conceptual refs

When implementation_scope = solution, ModelPackage must set solution_ref and conceptual_implementation_ref.


*adr_ref:* `ADR-045`

### INV-043: genesis_kind consistent with external_class_refs

genesis_kind=external requires at least one external_class_refs entry; genesis_kind=native forbids external_class_refs.


*adr_ref:* `ADR-045`

### INV-044: inverse_label required when RelationTerm not symmetric

A RelationTerm that is not symmetric must declare inverse_label.


*adr_ref:* `ADR-045`

### INV-045: LogicalAttribute max cardinality >= min

When both minimum_cardinality and maximum_cardinality are set on a LogicalAttribute, maximum_cardinality must be >= minimum_cardinality.


*adr_ref:* `ADR-045`

### INV-046: ConceptualEntity parent_concept_ref acyclic

ConceptualEntity.parent_concept_ref must not form a self-reference or cycle.


*adr_ref:* `ADR-045`

### INV-047: TechnicalAsset parent_ref acyclic

TechnicalAsset.parent_ref must not form a self-reference or cycle.


*requirement_refs:* `DAMS-REQ-PDM-006.c1`

*adr_ref:* `ADR-045`

### INV-048: selected attributes belong to selected entity

Each SelectedAttribute.logical_attribute_ref must identify an attribute of the SelectedEntity.logical_entity_ref.


*adr_ref:* `ADR-045`

### INV-049: compatibility_mode requires baseline when not none

When DataModelBinding.compatibility_mode is set and is not none, compatibility_baseline_ref must be present.


*adr_ref:* `ADR-045`

### INV-050: element_id unique within package document

element_id values must be unique across all objects in a ModelPackage (or binding) YAML document.


*adr_ref:* `ADR-045`

### INV-051: mapping_cardinality matches endpoint counts

mapping_cardinality must be consistent with the number of source_refs and target_refs (one_to_one ⇒ 1/1; one_to_many ⇒ 1/≥1; many_to_one ⇒ ≥1/1; many_to_many ⇒ ≥1/≥1).


*adr_ref:* `ADR-045`

### INV-052: LogicalAttribute.owner_entity_ref equals containing entity

When LogicalAttribute is inlined under LogicalEntity.attributes, owner_entity_ref must equal the parent entity element_id (containment equality; ADR-050).


*adr_ref:* `ADR-050`

### INV-053: Relationship ends are conceptual or logical entities

Relationship.source_entity_ref and target_entity_ref must resolve to a ConceptualEntity or LogicalEntity in the package (not attributes or technical assets).


*adr_ref:* `ADR-045`

См. также: [ADR-045](../adr/ADR-045-executable-constraint-matrix.md), [inventory report](constraint-matrix-inventory-report.md), [adding-an-invariant](../guides/adding-an-invariant.md).
