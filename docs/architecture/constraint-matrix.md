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
**registry size:** 27  
**invariants:** 27

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

См. также: [ADR-045](../adr/ADR-045-executable-constraint-matrix.md), [inventory report](constraint-matrix-inventory-report.md), [adding-an-invariant](../guides/adding-an-invariant.md).
