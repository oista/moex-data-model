# MOEX DAMS v0.1

**Reference specification** корпоративной модели данных MOEX, выраженная на LinkML  
(`ModelingStandard` = LinkML, `ReferenceSpecification` = MOEX DAMS 0.1).

Нормативная архитектура платформы: [`docs/architecture/MODELING_ARCHITECTURE.md`](../docs/architecture/MODELING_ARCHITECTURE.md).  
Этот каталог — **временный** путь исходников; целевое размещение после vertical slice — `model-assets/specifications/moex-dams/0.1/` (см. [`docs/architecture/app_model.md`](../docs/architecture/app_model.md)).

## Смысл уровней

| Уровень | Класс / артефакт |
|---|---|
| Spec root (`tree_root`) | `MOEXModelRepository` в `schemas/moex-dams.yaml` |
| Типичный документ решения | `ModelPackage` (conceptual / logical / physical) |
| Пример implementation | `examples/trading-solution-model.yaml` |

## Состав

- `schemas/moex-types.yaml` — типы и enum.
- `schemas/moex-registries.yaml` — ссылочные проекции внешних справочников.
- `schemas/moex-governance.yaml` — ownership, lifecycle, классификация, provenance.
- `schemas/moex-core.yaml` — концептуальный, логический и физический уровни, mappings.
- `schemas/moex-integration.yaml` — проекция потоков из Clinkr и семантические bindings.
- `schemas/moex-analytics.yaml` — опциональные метрики и измерения.
- `schemas/moex-contract-binding.yaml` — модельная дочерняя спецификация дата-контракта.
- `schemas/moex-dams.yaml` — корневая схема (`tree_root: MOEXModelRepository`).
- `examples/trading-solution-model.yaml` — пример артефакта модели решения.
- `publish.yaml` — манифест для Publication Viewer.

## Проверка

```bash
pip install linkml
cd schemas
linkml-lint moex-dams.yaml
gen-json-schema moex-dams.yaml > ../generated/moex-dams.schema.json
```

Публикация в статическом viewer (из корня репозитория): см. [`viewer/README.md`](../viewer/README.md) и корневой `README.md`.

## Статус

Версия `0.1.0` — архитектурный прототип. Межобъектные правила (разрешимость внешних ссылок, наследование классификации, согласованность Clinkr/EAM и проверка физической реализации) выполняются specification-модулем DAMS (`specification-dams` в целевом дереве) поверх базовой LinkML-валидации — не «второй рукописной копией» классов в kernel.
