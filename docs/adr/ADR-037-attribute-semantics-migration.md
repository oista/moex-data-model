---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-037: Миграция семантики LogicalAttribute

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-034](ADR-034-lightweight-conceptual-property.md), [ADR-031](ADR-031-technical-asset-registry.md)

## Context

Нужно перенести представление атрибутов в `DataType`/`ValueDomain` без потери данных
и без автосоздания ConceptualProperty.

## Decision

- Скрипт `scripts/migrate_logical_attribute_semantics.py` (ruamel.yaml, идемпотентный).
- `--apply`: группировка по (`logical_type`, `format_pattern`, `unit_code`,
  `value_set_ref`, `timezone_policy`); создать DataType/ValueDomain; проставить
  `data_type_ref`/`value_domain_ref`; пометить созданные объекты тегом `generated`
  в `tags` (слота `annotations` нет — как transitional в TechnicalAsset).
- `--propose`: кандидаты ConceptualProperty в отчёт и `proposed-properties.yaml`;
  модель не менять. Автосоздание свойств **отключено**.
- `moex-dams-full.yaml` — denylist (сгенерированный дамп); только регенерация.
- `integrity_digest`: пересчёт только fixtures/demo; иначе — политика новой ревизии
  (зависит от хвоста фазы 1 п.5; до закрытия — не угадывать baseline).
- Атрибуты без концептуальной пары остаются валидными навсегда (вариант B).
