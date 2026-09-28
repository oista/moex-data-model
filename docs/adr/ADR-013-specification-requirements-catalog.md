---
status: Proposed
version: "0.1"
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
- Каждое требование: код `{SECTION}-{NNN}`, уровень (`it_solution` в v0), раздел
  (LDM/PDM/REF/ATR/FLW/CLS/GEN), русская `statement`, набор `formal_checks`
  (kinds в духе LinkML constraints + опциональный `diagnostic_code`).
- Подключение `formal_checks` к assess pipeline **отложено**; коды — мост к
  существующим диагностикам.
- Viewer: корень «Требования» после «Спецификация» — уровень «ИТ-решения» с
  четырьмя вкладками: каталог требований, required-only схема, скелет
  ModelPackage и кураторский пример.

## Consequences

- Регенерация contracts включает новые классы.
- Каталог валидируется LinkML отдельно от ModelPackage assess.
- Авторы дополняют `requirements/*.yaml` без правки markdown-only реестра.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Sidecar YAML вне LinkML | нет typed contracts / единой схемы |
| Hardcode в viewer | нет Git-reviewable source of truth |
| Требования внутри ModelPackage | смешивает норму спецификации с телом решения |
| OWL/SHACL как реестр требований | другой носитель; не YAML authoring (ADR-010) |
| Только LinkML `class.rules` | нет кода раздела, уровня, человеческой формулировки |

## Related

- ADR-001 (LinkML YAML canonical), ADR-007 (validation stack), ADR-010
