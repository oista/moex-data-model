---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-056: Requirements backbone (normative modeling rules)

**Date:** 2026-10-27  
**Status:** Proposed (PR-0…PR-2 landed; PR-4/PR-5/PR-6 on stack `feat/requirements-backbone-pr4-pr5-pr6`; PR-3 parallel)  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Amends:** [ADR-013](ADR-013-specification-requirements-catalog.md) (code pattern `{SECTION}-{NN}`/`{NNN}`; section `CDM`; optional empty `formal_checks`; `obligation` / `responsible_role`)  
**Related:** [ADR-013](ADR-013-specification-requirements-catalog.md), [ADR-021](ADR-021-dams-implementation-profile-and-levels.md), [ADR-023](ADR-023-governed-property-cascade.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-026](ADR-026-cmd-entity-metamodel.md), [ADR-029](ADR-029-cdm-from-er-sketch-and-realization.md), [ADR-045](ADR-045-executable-constraint-matrix.md), [ADR-046](ADR-046-typed-mapping-endpoints.md), [ADR-048](ADR-048-topology-ownership.md), [ADR-051](ADR-051-dams-schema-compatibility.md)  
**Inventory:** [requirements-inventory.md](../migration/requirements-inventory.md)  
**Plan:** `.cursor/plans/moex-data-model_requirements_backbone_*.plan.md` (workspace)

## Context

The machine-readable catalogs

- [`it-solution-requirements.yaml`](../../model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml) (48 entries)
- [`conceptual-model-requirements.yaml`](../../model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml) (9 entries)

grew as an executable Wave-1/Wave-2 assess surface (GEN / LDM / ATR / REF / PDM / FLW / CLS / CM-*). Separately, corporate normative modeling rules fix a **backbone** of 21 codes:

| Prefix | Scope | Codes |
|---|---|---|
| CDM | Conceptual model | CDM-01, CDM-02 |
| LDM | Logical / IT-solution model | LDM-01 … LDM-13 |
| PDM | Physical model (integration surface) | PDM-01, PDM-02 |

Those normative codes **do not match** current DAMS codes by meaning (e.g. normative `LDM-01` ≠ catalog `LDM-001`). The catalog also mixes (1) modeling obligations, (2) schema/shape invariants, and (3) soft quality warnings. Assess today ignores `lifecycle_status` when loading the IT-solution catalog, so deprecation alone does not stop enforcement.

## Decision

### D1. Backbone is the requirements catalog spine

The 21 normative rules are the **spine** of the DAMS requirements catalog. Codes, obligation class, and responsible role come from the normative document (minor wording edits allowed later without reshaping the series).

| Obligation (normative) | Catalog / assess |
|---|---|
| ОБЯЗАТЕЛЬНО | `obligation: mandatory`, check severity `error` when automated |
| РЕКОМЕНДУЕТСЯ | `obligation: recommended`, check severity `warning` when automated |

Manual rules (no executable `formal_checks`) remain valid per [ADR-013](ADR-013-specification-requirements-catalog.md): absence of checks means human-review, not silence.

Responsible roles from the normative table (catalog slot `responsible_role` in PR-1):

| Normative label | Slot value |
|---|---|
| Архитектура данных | `data_architecture` |
| ИТ-владелец | `it_owner` |
| бизнес-владелец | `business_owner` |

#### Backbone catalog (21)

Statements are the normative text (minor edits allowed later without reshaping the series). `formal_checks` may be empty until PR-5 / PR-7.

| Code | Obligation | Role | Statement (normative) |
|---|---|---|---|
| CDM-01 | mandatory | data_architecture | Для каждого сущности концептуальной модели внесено соответствующее определение глоссария, раскрывающее единый(общий) для Группы бизнес-смысл термина, независимо от предметной области и способов реализации |
| CDM-02 | mandatory | data_architecture | Полностью описаны базовые типы связей между сущностями КМД — «Входит в состав», «Является разновидностью» |
| LDM-01 | mandatory | it_owner | Логическая модель данных (ЛМД) определена на уровне ИТ-решения |
| LDM-02 | mandatory | it_owner | ЛМД соответствует актуальной версии принятой спецификации. Версия спецификации указана в описании модели |
| LDM-03 | mandatory | it_owner | Модель ИТ-решения зарегистрирована в Дата-каталоге |
| LDM-04 | mandatory | business_owner | Для каждой сущности ЛМД должно быть внесено определение бизнес-термина глоссария, раскрывающее его смысл, применительно к описываемому ИТ-решению (включая ссылку на нормативную документацию, при её наличии) |
| LDM-05 | mandatory | business_owner | Для каждой сущности ЛМД описаны атрибуты, необходимые для однозначного представления её бизнес-смысла, идентификации, характеристик, состояния и участия в предусмотренных бизнес-процессах |
| LDM-06 | mandatory | business_owner | Для каждой сущности ЛМД определен состав атрибутов уникального идентификатора. Приоритетный порядок выбора идентификатора – бизнес ключ, натуральный ключ, суррогатный ключ (при отсутствии перечисленных выше альтернатив) |
| LDM-07 | mandatory | business_owner | Полностью описаны существующие базовые типы связей между сущностями — «Входит в состав», «Является разновидностью», «Ссылается на справочник» |
| LDM-08 | mandatory | business_owner | В дополнение к описанию базовых типов связей между сущностями ЛМД, описаны остальные типы связей (согласно справочнику типов) |
| LDM-09 | mandatory | it_owner | Для каждой сущности ЛМД указан Класс данных. В случае смешанной классификации сущности — Класс данных указан для её атрибутов |
| LDM-10 | mandatory | it_owner | Для каждой сущности ЛМД указан Класс конфиденциальности данных. В случае смешанной классификации сущности — Класс конфиденциальности указан для её атрибутов |
| LDM-11 | mandatory | business_owner | Для каждой сущности ЛМД указан владелец данных. В случае нескольких владельцев — владелец указан для атрибутов сущности |
| LDM-12 | mandatory | it_owner | Для каждой сущности ЛМД указана система-источник. При различии источников отдельных атрибутов источники указаны на уровне соответствующих атрибутов |
| LDM-13 | recommended | it_owner | Для каждой сущности ЛМД указана Классификация ИОД. В случае смешанной классификации – указывается более высокая степень чувствительности, либо размечаются отдельные атрибуты |
| PDM-01 | mandatory | it_owner | В ФМД описаны все сущности и атрибуты, через которые ИТ-решение выступает поставщиком данных в интеграциях |
| PDM-02 | mandatory | it_owner | Для каждого атрибута сущности ФМД, несущего бизнес-смысл, указана связь с атрибутом сущности ЛМД |

### D2. Disposition of the 57 current entries

| Group | Count | Disposition |
|---|---:|---|
| **A** Dissolve into backbone | 14 | Executable checks move under new codes; old rows `superseded` |
| **B** Keep as local extensions | 2 | Remain in catalog with new stable codes if number collides |
| **C** Leave catalog; keep enforcement | 31 | Schema `required`, Python rules, and/or `INV-*` (constraint matrix) |
| **D** Remove | 10 | Drop as modeling requirements after deprecation window |

**Group A:** GEN-001, GEN-002, GEN-003, LDM-002, LDM-003, LDM-004, LDM-005, REF-003, PDM-003, PDM-004, FLW-001, CM-CON-001, CM-REF-002, CM-CON-002.

**Group B:** LDM-006 (conceptual alignment), REF-002 (relationship cardinality). Final codes decided in PR-10 (number collision with backbone `LDM-06`).

**Group C:** PDM-001, PDM-002, PDM-005…PDM-020, ATR-001, ATR-006, REF-001, FLW-002…FLW-005, CM-GEN-001, CM-GEN-002, CM-PDM-000, CM-PROP-001, CM-REF-001, CM-CON-003.

**Group D:** GEN-004, LDM-001, LDM-007, LDM-008, ATR-002, ATR-004, ATR-005, ATR-007, CLS-001, CLS-002.

### D3. Check handover map (Group A → backbone)

`superseded_by` is a **single** reference. When one old row feeds several backbone codes, the slot points at the **primary** successor; the full fan-out is this table (authoritative for migration).

| Old code | Primary `superseded_by` | Also feeds | Notes |
|---|---|---|---|
| GEN-001 | LDM-02 (`api_version`) | LDM-11 (`data_owner_ref`) | Identity slots → schema `required` (PR-8) |
| GEN-002 | LDM-01 | — | Solution binding |
| GEN-003 | LDM-01 | — | Non-empty package; whether ≥1 `LogicalEntity` is PR-10 |
| LDM-002 | LDM-04 (definition) | LDM-11 (ownership) | title/name/lifecycle → schema (PR-8) |
| LDM-003 | LDM-09 (`data_class`) | LDM-10 (`governance_classification`) | `entity_type` / `business_importance` obligation dropped (PR-10) |
| LDM-004 | LDM-06 | — | Key composition; `identity_rule` text not mandatory (PR-10) |
| LDM-005 | LDM-05 | — | ≥1 attribute floor |
| REF-003 | LDM-07 | LDM-08 | `relationship_kind` for active links |
| PDM-003 | PDM-02 | — | Entity↔carrier mapping |
| PDM-004 | PDM-02 | — | Field↔attribute mapping |
| FLW-001 | PDM-01 | — | Soft coverage vs integrations |
| CM-CON-001 | CDM-01 | — | Entity definition / description |
| CM-REF-002 | CDM-02 | — | Relation terms |
| CM-CON-002 | CDM-02 | — | Dependent / composition via tier |

Number lookalikes (must not be confused during coexistence):

| Old | Backbone | Collision risk |
|---|---|---|
| `LDM-001` (context / role) | `LDM-01` (LMD at IT-solution) | Different meaning; Group D vs new spine |
| `LDM-006` (alignment) | `LDM-06` (identifier) | Group B needs a new local code (PR-10) |

### D4. Series PR table

| PR | Theme | Touches schemas / `generated/`? |
|---|---|---|
| **PR-0** | This ADR + [requirements-inventory.md](../migration/requirements-inventory.md) | **No** |
| **PR-1** | Requirements metamodel: code pattern `{2,3}`, section `CDM`, `formal_checks` min 0, `obligation` / `responsible_role`; regen | Schema + regen |
| **PR-2** | Runner skips `deprecated` / `superseded` / `rejected` | Code + tests |
| **PR-3** | INV for PDM-005, 007, 010, 015, 017, 019 | Matrix + fixtures |
| **PR-4** | Add 21 backbone rows (statements only, no checks yet) | Catalog data |
| **PR-5** | Move Group A checks onto backbone; old rows `superseded` | Catalog data + tests |
| **PR-6** | Docs / explorer / export consumers | Docs (+ export tests) |
| **PR-7** | Schema gaps for LDM-03 / 09(attr) / 12 / 13 (decisions) | Schema (later) |
| **PR-8** | Move `slot_required` obligations into LinkML `required` | Schema; data separate commit if needed |
| **PR-9** | Retire Group C from catalog; rebind matrix / aliases | Catalog + matrix + Python codes |
| **PR-10** | Group D / B / GEN-003 / glossary wording / diagnostic policy; final cleanup | Decisions + cleanup |

`check_all` (and listed gates) must be green **on each PR branch separately**. No combined “all PRs green” tree as proof of intermediate validity ([multi-pr-series](../../.cursor/rules/multi-pr-series.mdc)). No PR-5-style schema+data+regen exception is claimed for this series.

### D5. Deferred to PR-7…PR-10 (do not decide in PR-0…PR-6)

- Schema slots for LDM-03 (data-catalog registration), LDM-09 on attributes, LDM-12 (source system on logical), LDM-13 (ИОД vs `sensitivity_term_refs`).
- Whether GEN-003 under LDM-01 requires ≥1 `LogicalEntity`.
- CDM-01 / LDM-04 wording vs ADR-025 (definition on element; glossary is a **view**, not a mandatory sibling term record).
- Dropping mandatory `identity_rule`, `entity_type`, `business_importance`.
- Confirming each Group D deletion after assess impact.
- Renaming Group B `LDM-006` / keeping REF-002 as recommended.
- Deprecating `security_classification` (CLS-002 overlap with `governance_classification`).
- Renaming diagnostic codes to `DAMS-INV-*` vs keeping `DAMS-REQ-*` stable.

## Consequences

- Normative backbone becomes the human-facing requirements spine; assess and INV remain the executable subset.
- Coexistence of old three-digit and new two-digit codes requires PR-1 pattern widening before PR-4 insert.
- Runner must honour lifecycle (PR-2) before mass `superseded` (PR-5) or assess will double-fire.
- Group C must have INV homes (PR-3) before catalog deletion (PR-9).

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Renumber backbone to three-digit DAMS codes | Breaks normative document identity |
| Keep all 57 as peer requirements | Dilutes normative spine; mixes invariants with modeling rules |
| Big-bang replace in one PR | Violates multi-PR series; breaks intermediate assess |
| Encode process-only LDM-03 as body assess today | No slot; belongs in publication/process gate until PR-7 |

## Related

- Inventory: [requirements-inventory.md](../migration/requirements-inventory.md)
- Catalog metamodel: [moex-requirements.yaml](../../model-assets/specifications/moex-dams/0.1/schemas/moex-requirements.yaml)
- Body assess doc: [IT_SOLUTION_MODEL_REQUIREMENTS.md](../architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md)
