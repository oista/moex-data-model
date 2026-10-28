# Requirements backbone inventory

**Date:** 2026-10-27  
**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md)  
**Related:** [ADR-013](../adr/ADR-013-specification-requirements-catalog.md), [ADR-045](../adr/ADR-045-executable-constraint-matrix.md)  
**Scope:** where each current `SpecificationRequirement` is enforced today, disposition under ADR-056, and consumer touchpoints before the requirements-backbone series.

## Catalog sources

| Catalog | Path | Count |
|---|---|---:|
| IT-solution | [`it-solution-requirements.yaml`](../../model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml) | 63 (48 legacy + 15 backbone LDM/PDM) |
| Conceptual | [`conceptual-model-requirements.yaml`](../../model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml) | 11 (9 legacy + CDM-01/02) |
| **Total** | | **74** |

Metamodel: [`moex-requirements.yaml`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-requirements.yaml).  
Body assess loader: `packages/specification-dams/src/moex_dams/rules/formal_checks.py` → `load_it_solution_catalog` (IT-solution file **only**; conceptual catalog is export / documentation / status tests).

### Enforcement legend

| Tag | Meaning |
|---|---|
| `runner` | Executable via `formal_checks` kinds other than `custom` (`slot_required`, `conditional_branch`, `ref_resolves`, `definition_resolvable`, `at_least_one_slots`, …) |
| `custom-skip` | Catalog row has `kind: custom`; runner **skips**; real check is elsewhere |
| `python` | Dedicated rule module emits diagnostics |
| `INV` | Row referenced from [`constraint-matrix.yaml`](../../model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml) |
| `schema` | Likely / intended LinkML `required` or shape (verify in PR-8) |

## Disposition summary

| Group | Meaning | Count |
|---|---|---:|
| A | Dissolve into backbone codes | 14 |
| B | Keep as local extension | 2 |
| C | Remove from catalog; keep enforcement | 31 |
| D | Remove entirely (after window) | 10 |

## IT-solution catalog (48)

| Code | Title | Checks / kinds | Enforced today | Group | Destination | Consumers |
|---|---|---|---|---|---|---|
| GEN-001 | Идентичность и ответственность пакета | 7 `slot_required` | `runner` (+ cascade placeholder lint `GEN-001`) | A | LDM-02 (`api_version`); LDM-11 (`data_owner_ref`); identity → schema PR-8 | `formal_checks.py`; `test_formal_checks.py`; `test_cascade_resolver.py` |
| GEN-002 | Привязка к ИТ-решению | 2 | `runner` | A | LDM-01 | `formal_checks.py` |
| GEN-003 | Непустой состав модели | 1 | `runner` | A | LDM-01 (LogicalEntity floor = PR-10) | `formal_checks.py` |
| GEN-004 | Носители данных связаны со смыслом | 1 | `runner` | D | Drop (duplicate of PDM-003 / PDM-02) | `formal_checks.py` |
| LDM-001 | Контекст и роль данных | 3 | `runner` | D | Drop; slots become optional unless schema requires | `formal_checks.py` |
| LDM-002 | Обозначение и ответственность сущности | 5 | `runner` (`definition_resolvable`, ownership `effective`) | A | LDM-04; LDM-11; naming → schema PR-8 | `formal_checks.py`; `definitions.py`; `test_definition_resolver.py` |
| LDM-003 | Классификация сущности | 4 | `runner` (`governance` `effective`) | A | LDM-09; LDM-10; drop entity_type/importance obligation PR-10 | `formal_checks.py`; cascade |
| LDM-004 | Правило идентичности | 1 | `runner` | A | LDM-06 | `formal_checks.py` |
| LDM-005 | Наличие характеристик | 1 | `runner` | A | LDM-05 | `formal_checks.py` |
| LDM-006 | Связь с корпоративными понятиями | 1 | `runner` | B | Keep; **recode** in PR-10 (collides with backbone LDM-06) | `formal_checks.py`; ADR-025 / ADR-029 |
| LDM-007 | Семантическая включённость | 1 | `runner` | D | Drop | `formal_checks.py` |
| LDM-008 | Полнота реализации зависимых концептов | 1 warning | `runner` | D | Drop (ADR-029 soft) | `formal_checks.py` |
| ATR-001 | Основные свойства атрибута | 4 (`slot_required` + `custom`) | `runner` + `python` (`semantic_layer` type) | C | Schema `required` + SEM checks | `formal_checks.py`; `semantic_layer.py` |
| ATR-002 | Именование атрибута | 1 warning | `runner` | D | Drop (linter-class) | `formal_checks.py` |
| ATR-004 | Дополнительные свойства по типу атрибута | 1 warning | `runner` | D | Drop | `formal_checks.py` |
| ATR-005 | Отображение атрибута на реализацию | 2 | `runner` | D | Drop (reverse of PDM-02) | `formal_checks.py` |
| ATR-006 | Представление атрибута (тип или домен) | 1 `custom` | `custom-skip` → `python` `DAMS-SEM-ATTR-TYPE` | C | Keep SEM rule; drop catalog row | `semantic_layer.py`; `test_semantic_layer.py` |
| ATR-007 | concept_ref опционален | 1 `custom` | Negation / test contract | D | Drop; keep `test_missing_concept_ref_is_silent` | `test_semantic_layer.py` |
| REF-001 | Концы связи | 4 | `runner` | C | Schema / ref rules | `formal_checks.py`; `references.py` |
| REF-002 | Кардинальность связи | 1 | `runner` | B | Keep as recommended (PR-10) | `formal_checks.py` |
| REF-003 | Тип логической связи | 1 warning | `runner` | A | LDM-07 / LDM-08 | `formal_checks.py` |
| PDM-001 | Основные свойства носителя данных | 7 | `runner` | C | Schema `required` (PR-8) | `formal_checks.py` |
| PDM-002 | Основные свойства узла схемы | 3 | `runner` | C | Schema `required` (PR-8) | `formal_checks.py` |
| PDM-003 | Отображение сущности и носителя | 1 | `runner` | A | PDM-02 | `formal_checks.py`; ADR-046 |
| PDM-004 | Отображение узла схемы и атрибута | 1 | `runner` | A | PDM-02 | `formal_checks.py`; ADR-046 |
| PDM-005 | Уникальность ключа технического актива | 1 `custom` | `python` + **INV-059** | C | INV-059 | `technical_assets.py`; `test_technical_asset_checks.py` |
| PDM-006 | Иерархия parent_ref без циклов | 1 `custom` | `python` + **INV-047** | C | INV-047 | `technical_assets.py`; matrix |
| PDM-007 | Допустимые asset_kind по подклассу | 1 `custom` | `python` + **INV-060** | C | INV-060 | `technical_assets.py` |
| PDM-008 | Запрет direction для контейнеров | 1 `custom` | `python` + **INV-018** | C | INV-018 | `technical_assets.py`; matrix |
| PDM-009 | Типы концов Mapping | 1 `custom` | `python` + **INV-033…036** (+ field resolve) | C | INV-033+ | `technical_assets.py`; `data_structure.py`; `test_mapping_endpoint_invariants.py` |
| PDM-010 | carrier_refs только на DataCarrier | 1 `custom` | `python` + **INV-061** | C | INV-061 | `technical_assets.py` |
| PDM-011 | operation требует interface_ref | 1 `custom` | `python` + **INV-016** | C | INV-016 | `technical_assets.py`; matrix |
| PDM-012 | in_memory без location | 1 `custom` | `python` + **INV-015** | C | INV-015 | `technical_assets.py`; matrix |
| PDM-013 | Уникальность local_key | 1 `custom` | `python` + **INV-022** | C | INV-022 | `data_structure.py`; matrix |
| PDM-014 | Ацикличность SchemaNode | 1 `custom` | `python` + **INV-020** | C | INV-020 | `data_structure.py`; matrix |
| PDM-015 | Корень DataStructure | 1 `custom` | `python` + **INV-062** | C | INV-062 | `data_structure.py`; `test_data_structure_checks.py` |
| PDM-016 | Реляционные признаки только relational | 1 `custom` | `python` + **INV-021** | C | INV-021 | `data_structure.py`; matrix |
| PDM-017 | Границы кратности узла | 1 `custom` | `python` + **INV-063** | C | INV-063 | `data_structure.py` |
| PDM-018 | message_refs по виду AccessPoint | 1 `custom` | `python` + **INV-017 / INV-019** | C | INV-017/019 | `data_structure.py`; matrix |
| PDM-019 | Payload Message | 1 `custom` | `python` + **INV-064** | C | INV-064 | `data_structure.py` |
| PDM-020 | Форма узла по node_kind | 1 `custom` | `python` + **INV-012 / INV-013** | C | INV-012/013 | `data_structure.py`; matrix |
| CLS-001 | Независимость осей классификации | 1 warning | `runner` | D | Drop | `formal_checks.py` |
| CLS-002 | Режим защиты данных | 1 warning | `runner` | D | Drop; slot deprecation separate (PR-10+) | `formal_checks.py` |
| FLW-001 | Потоки через границы решений | 1 warning | `runner` | A | PDM-01 | `formal_checks.py` |
| FLW-002 | integration_ref по снимку каталога | 1 `custom` | `python` + **INV-038** | C | INV-038 / `catalog_topology.py` | `catalog_topology.py`; `test_catalog_topology.py` |
| FLW-003 | catalog_operation_ref в снимке | 1 `custom` | `python` + **INV-039** | C | INV-039 | same |
| FLW-004 | bound_catalog_revision | 1 `custom` | `python` + **INV-040** | C | INV-040 | same |
| FLW-005 | DataModelBinding.catalog_revision | 1 `custom` | `python` + **INV-041** | C | INV-041 | same |

## Conceptual catalog (9)

| Code | Title | Lifecycle | Checks / kinds | Enforced today | Group | Destination | Consumers |
|---|---|---|---|---|---|---|---|
| CM-GEN-001 | Идентичность пакета КМД | draft | 6 `slot_required` | docs / export; codes `CM-*` outside IT-solution `code` pattern | C | Schema + `dams_levels` / STRUCT | `test_export_requirements.py`; `test_requirement_statuses.py` |
| CM-GEN-002 | Область enterprise-conceptual | proposed | 1 | `python` levels (`DAMS-LEVEL-002`) | C | `dams_levels.py` | `test_dams_levels.py` |
| CM-CON-001 | Концептуальная сущность | approved | 4 | docs intent; entity checks overlap Python | A | CDM-01 | `conceptual_entity.py` (partial) |
| CM-REF-001 | Концы связей КМД | draft | 4 | ref diagnostics | C | `references.py` / STRUCT | refs rules |
| CM-CON-002 | entity_tier primary/dependent | proposed | 1 `custom` | `python` `DAMS-CM-TIER-*` | A | CDM-02 | `conceptual_entity.py`; `test_cmd_entity_metamodel.py` |
| CM-CON-003 | genesis external/native | approved | 1 `custom` | `python` `DAMS-CM-GENESIS-*` + INV-043 aliases | C | keep Python / INV | `conceptual_entity.py` |
| CM-REF-002 | RelationTerm | approved | 1 `custom` | `python` `DAMS-CM-RELTERM-*` + INV-044 | A | CDM-02 | `relation_terms.py` |
| CM-PDM-000 | Запрет технического слоя | approved | 1 `custom` | `python` `DAMS-LEVEL-003` | C | `dams_levels.py` | `test_dams_levels.py` |
| CM-PROP-001 | ConceptualProperty только enterprise | approved | 1 `custom` | `python` `DAMS-SEM-PROP-SCOPE` | C | `semantic_layer.py` | `test_semantic_layer.py` |

## Constraint-matrix `requirement_refs` (today)

Aliases also in `packages/specification-dams/src/moex_dams/rules/constraint_matrix.py` (`INV_*_DIAGNOSTIC_ALIASES`).

| INV | `requirement_refs` (diagnostic codes) | Catalog code |
|---|---|---|
| INV-012 | DAMS-REQ-PDM-020.c1/c2 | PDM-020 |
| INV-013 | DAMS-REQ-PDM-020.c3/c4 | PDM-020 |
| INV-015 | DAMS-REQ-PDM-012.c1 | PDM-012 |
| INV-016 | DAMS-REQ-PDM-011.c1 | PDM-011 |
| INV-017 | DAMS-REQ-PDM-018.c1 | PDM-018 |
| INV-018 | DAMS-REQ-PDM-008.c1 | PDM-008 |
| INV-019 | DAMS-REQ-PDM-018.c2 | PDM-018 |
| INV-020 | DAMS-REQ-PDM-014.c1 | PDM-014 |
| INV-021 | DAMS-REQ-PDM-016.c1 | PDM-016 |
| INV-022 | DAMS-REQ-PDM-013.c1 | PDM-013 |
| INV-033… | DAMS-REQ-PDM-009.c1 | PDM-009 |
| INV-034 | DAMS-REQ-PDM-009.c2 | PDM-009 |
| INV-047 | DAMS-REQ-PDM-006.c1/c2 | PDM-006 |
| INV-038 | DAMS-REQ-FLW-002.c1 | FLW-002 |
| INV-039 | DAMS-REQ-FLW-003.c1 | FLW-003 |
| INV-040 | DAMS-REQ-FLW-004.c1 | FLW-004 |
| INV-041 | DAMS-REQ-FLW-005.c1 | FLW-005 |
| INV-042 | DAMS-LEVEL-004/005 | levels (not catalog PDM) |
| INV-043 | DAMS-CM-GENESIS-001/002 | CM-CON-003 family |
| INV-044 | DAMS-CM-RELTERM-002 | CM-REF-002 |

**Missing INV (PR-3):** closed — PDM-005→INV-059, PDM-007→INV-060, PDM-010→INV-061, PDM-015→INV-062, PDM-017→INV-063, PDM-019→INV-064.

## Metamodel blockers (PR-1)

Observed before series coding:

| Constraint | Impact |
|---|---|
| `code` pattern `^(LDM\|PDM\|REF\|ATR\|FLW\|CLS\|GEN)-[0-9]{3}$` | Blocks `CDM-*` and two-digit `LDM-01` |
| No `CDM` in `RequirementSectionEnum` | Same |
| `formal_checks` `minimum_cardinality: 1` | Blocks manual backbone rows (LDM-03, …) |
| `catalog_validate.py` `CATALOG-CHECKS-MISSING` | Same constraint in the semantic gate; must allow empty checks in PR-1 |
| `catalog_validate.py` `CODE_PATTERN` | Duplicates the YAML `code` pattern; update in the same PR as the schema |
| No `obligation` / `responsible_role` slots | Normative classification / owner not representable |
| `superseded_by` single-valued | Fan-out only in ADR table (D3) |
| Runner ignores `lifecycle_status` | PR-2 required before mass supersede |

Note: conceptual catalog already uses `CM-*` codes that do not match the IT-solution `code` pattern; validate-requirements baseline behaviour must be recorded in PR-1 before widening the pattern.

## Test / docs consumers (non-exhaustive)

| Path | Role |
|---|---|
| `packages/specification-dams/tests/test_formal_checks.py` | Body assess for catalog rows |
| `packages/specification-dams/tests/test_catalog_validate.py` | Catalog schema gate |
| `packages/specification-dams/tests/test_export_requirements.py` | Export both catalogs |
| `packages/specification-dams/tests/test_requirement_statuses.py` | Lifecycle enums vs catalog |
| `packages/specification-dams/tests/test_definition_resolver.py` | LDM-002 definition checks |
| `packages/specification-dams/tests/test_technical_asset_checks.py` | PDM-005…012 family |
| `packages/specification-dams/tests/test_data_structure_checks.py` | PDM-013…020 family |
| `packages/specification-dams/tests/test_mapping_endpoint_invariants.py` | PDM-009 |
| `packages/specification-dams/tests/test_catalog_topology.py` | FLW-002…005 |
| `packages/specification-dams/tests/test_cmd_entity_metamodel.py` | CM-CON / CM-REF |
| `docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md` | Human Wave-1/2 catalog narrative |
| `docs/architecture/constraint-matrix.md` | INV ↔ requirement_refs prose |
| `docs/superpowers/specs/2026-09-28-dams-requirements-explorer-design.md` | Explorer tree by section |

## Backbone gaps closed / deferred in PR-7 (ADR-056)

| Backbone | Before PR-7 | PR-7 decision | Enforcement after PR-7 |
|---|---|---|---|
| LDM-03 | Manual (`formal_checks: []`); hoped-for catalog slot | **Stays manual** (publication / process gate); no slot | Human-review only |
| LDM-09 | Entity `slot_required` `data_class` only; no attribute slot | Cascade entity→attribute (inline-only); check effective on entity **or** every attribute | `runner` `ldm09_data_class` (PR-7d) |
| LDM-12 | Manual; no logical source-system slot | Slot `source_system_refs` + cascade; warning then error | `runner` `ldm12_source_system` (PR-7d/f) |
| LDM-13 | Manual; ИОД vocabulary unclear | Mapped to `sensitivity_term_refs`; **stays manual** until PR-10 | Human-review; executable later |

## Implications for migration

- PR-0 is documentation only: no catalog, schema, or `generated/` edits.
- Do not mark rows `superseded` until PR-2 lands (otherwise assess still fires old checks).
- Do not delete Group C rows until PR-3 INV coverage exists for the six PDM gaps.
- When statements of the normative 21 rules change slightly, edit PR-4 rows only; disposition groups stay stable.
- PR-7a is documentation only (amends ADR-023 / ADR-056); schema and cascade code follow in PR-7b…7f.
