---
status: Proposed
version: "0.2"
normative: false
supersedes: []
superseded_by: []
---

# ADR-013: Каталог требований к спецификации в DAMS LinkML

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Design:** [2026-09-28-dams-requirements-explorer-design.md](../superpowers/specs/2026-09-28-dams-requirements-explorer-design.md)

## Context

Нормативные MUST к модели ИТ-решения (`DAMS-F-*`) живут в markdown, а машинные
коды (`DAMS-STRUCT-*`, `DAMS-REF-*`) — в rule runner. Читателю publication viewer
нужен единый каталог: понятная формулировка + формальные проверки. В каноне
LinkML нет класса «Requirement catalog»; `class.rules` / `slot.required` задают
ограничения схемы, но не реестр корпоративных требований с кодами разделов.

## Decision

- Требования к reference specification — first-class сущности DAMS LinkML:
  `SpecificationRequirement`, `FormalCheck`, контейнер `RequirementCatalog`
  (модуль `moex-requirements.yaml`).
- Инстансы каталога — отдельный YAML под деревом DAMS (`requirements/…`),
  **не** вложены в solution `ModelPackage`.
- Каждое требование: код `{SECTION}-{NNN}`, уровень (`it_solution` /
  `conceptual_model`), раздел (LDM/PDM/REF/ATR/FLW/CLS/GEN), русская
  `statement` (норма для человека **без** сленга метамодели), `applies_to`,
  набор `formal_checks` с `diagnostic_code`, `severity`, `remediation`.
- **Каталог — источник структурированных правил.** Не каждая нормативная
  формулировка автоматически исполняема: `formal_checks` — исполняемое
  подмножество. Отсутствие `formal_checks` — не молчание, а зона
  human-review / manual.
- Каждая исполняемая проверка имеет стабильный diagnostic code и severity.
- **Assess wiring (v0.2):** `moex_dams.rules.formal_checks` подключён к
  `default_dams_rule_sets` / `assess_implementation`. Gate публикации
  композитный:
  **body-assess** (formal_checks + structural/refs) **+**
  **publication-contract** (ADR-019) **+** schema validation.
  Body-assess не дублирует naming/presence-секций Viewer; ADR-019 не
  доказывает identity_rule или classification.
- Viewer: корень «Требования» — уровни «Концептуальная модель»,
  «ИТ-решения», «Публикация».

### Severity phasing

| Category | Wave 1 | Wave 2 | Later |
|----------|--------|--------|-------|
| Package identity / EAM link | Error | Error | Error |
| Logical entity core metadata | Error | Error | Error |
| Identity rule | Error | Error | Error |
| Entity/attribute/physical mappings (with declared exceptions) | Error | Error | Error |
| Ref resolution / cardinality | Error | Error | Error |
| Naming | — | Warning | Error after baseline |
| Atomicity | — | Warning | Selective error |
| Currency/unit/timezone | — | Warning | Error by data class |
| entity_type/data_class conditionals | — | Warning | Error after calibration |
| DataFlow / integration | — | Warning | Error for critical flows |
| Security/regulatory | — | Warning | Error after policy alignment |
| Full logical↔physical completeness | — | Warning (needs state) | Error when state model exists |

`mapping_coverage_status: planned` требует `mapping_rationale` и **не** является
постоянным обходом для `lifecycle_status: active` (Wave 1: warning).

## Consequences

- Регенерация contracts включает новые классы и enums
  (`MappingCoverageStatusEnum`, `BusinessKeyKindEnum`, …).
- Каталог валидируется LinkML отдельно от ModelPackage assess; assess
  исполняет formal_checks.
- Авторы дополняют `requirements/*.yaml` без правки markdown-only реестра.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Sidecar YAML вне LinkML | нет typed contracts / единой схемы |
| Hardcode в viewer | нет Git-reviewable source of truth |
| Требования внутри ModelPackage | смешивает норму спецификации с телом решения |
| OWL/SHACL как реестр требований | другой носитель; не YAML authoring (ADR-010) |
| Только LinkML `class.rules` | нет кода раздела, уровня, человеческой формулировки |
| Дублировать body-checks в ADR-019 | смешивает presence публикации с семантикой тела |

## Related

- ADR-001 (LinkML YAML canonical), ADR-007 (validation stack), ADR-010,
  ADR-019 (publication contract inheritance)
