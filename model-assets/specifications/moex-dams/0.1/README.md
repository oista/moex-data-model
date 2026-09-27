# MOEX DAMS v0.1

**Reference specification** корпоративной модели данных MOEX, выраженная на LinkML  
(`ModelingStandard` = LinkML, `ReferenceSpecification` = MOEX DAMS 0.1).

Нормативная архитектура платформы: [`docs/architecture/MODELING_ARCHITECTURE.md`](../../../docs/architecture/MODELING_ARCHITECTURE.md).  
Конверт спецификации: [`specification.yaml`](specification.yaml).  
Пример implementation: [`trading-platform`](../../../implementations/solutions/trading-platform/).

## Смысл уровней

| Уровень | Класс / артефакт |
|---|---|
| Spec root (`tree_root`) | `MOEXModelRepository` в `schemas/moex-dams.yaml` |
| Типичный документ решения | `ModelPackage` (conceptual / logical / physical) |
| Пример implementation | `model-assets/implementations/solutions/trading-platform/` |

## Состав

- `specification.yaml` — kernel envelope (`ReferenceSpecification`).
- `schemas/moex-types.yaml` — типы и enum.
- `schemas/moex-registries.yaml` — ссылочные проекции внешних справочников.
- `schemas/moex-governance.yaml` — ownership, lifecycle, классификация, provenance.
- `schemas/moex-core.yaml` — концептуальный, логический и физический уровни, mappings.
- `schemas/moex-integration.yaml` — проекция потоков из Clinkr и семантические bindings.
- `schemas/moex-analytics.yaml` — опциональные метрики и измерения.
- `schemas/moex-contract-binding.yaml` — модельная дочерняя спецификация дата-контракта.
- `schemas/moex-dams.yaml` — корневая схема (`tree_root: MOEXModelRepository`).
- `examples/` — дополнительные instance fixtures (не trading-platform).
- `publish.yaml` — манифест Publication Viewer для тела спецификации.
- `architecture-catalog.yaml` — навигация sidebar viewer.

## Проверка

```bash
pip install linkml
cd schemas
linkml-lint moex-dams.yaml
gen-json-schema moex-dams.yaml > ../../../../generated/artifacts/moex-dams/0.1/moex-dams.schema.json
```

Или из корня репозитория: `make validate-schemas` / `make check`.  
Viewer: [`apps/viewer/README.md`](../../../../apps/viewer/README.md).

## Статус

Версия `0.1.0` — архитектурный прототип. Межобъектные правила выполняются `packages/specification-dams` поверх LinkML-валидации.
