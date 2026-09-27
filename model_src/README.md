# MOEX DAMS v0.1

Прототип метамодели описания корпоративной модели данных MOEX на LinkML.

## Состав

- `schemas/moex-types.yaml` — типы и enum.
- `schemas/moex-registries.yaml` — ссылочные проекции внешних справочников.
- `schemas/moex-governance.yaml` — ownership, lifecycle, классификация, provenance.
- `schemas/moex-core.yaml` — концептуальный, логический и физический уровни, mappings.
- `schemas/moex-integration.yaml` — проекция потоков из Clinkr и семантические bindings.
- `schemas/moex-analytics.yaml` — опциональные метрики и измерения.
- `schemas/moex-contract-binding.yaml` — модельная дочерняя спецификация дата-контракта.
- `schemas/moex-dams.yaml` — корневая схема.
- `examples/trading-solution-model.yaml` — пример артефакта модели решения.

## Проверка

```bash
pip install linkml
cd schemas
linkml-lint moex-dams.yaml
gen-json-schema moex-dams.yaml > ../generated/moex-dams.schema.json
```

## Статус

Версия `0.1.0` — архитектурный прототип. Межобъектные правила (разрешимость внешних ссылок, наследование классификации, согласованность Clinkr/EAM и проверка физической реализации) должны выполняться `dmr engine` поверх базовой LinkML-валидации.
