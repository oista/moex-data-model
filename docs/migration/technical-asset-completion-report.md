# TechnicalAsset migration — completion report

## Было → стало (классы и слоты)

| Было | Стало |
|---|---|
| `PhysicalObject` | иерархия `TechnicalAsset` → `DataCarrier` / `AccessPoint` / `DataContainer` / `ExecutionAsset` |
| `PhysicalObjectKindEnum` | `DataCarrierKindEnum`, `AccessPointKindEnum`, `DataContainerKindEnum`, `ExecutionAssetKindEnum` |
| `ModelPackage.physical_objects` | `data_carriers`, `access_points`, `data_containers`, `execution_assets` (Variant B) |
| `object_kind` | `asset_kind` |
| `physical_object_ref` | `carrier_ref` (`PhysicalField` → `DataCarrier`) |
| `physical_object_refs` | `carrier_refs` (`DataFlowEntityBinding`, `SelectedEntity`) |
| `native_schema_ref` | `structure_ref` (`HasStructure`) |
| (новый) | `asset_namespace` (не `DomainContext.namespace`) |
| transitional пометка | тег `tags: [transitional, namespace_heuristic]` (не `annotations`: отсутствует в схеме) |

## Выбор при неоднозначностях (раздел 5 плана)

| Место | Range / решение | Причина |
|---|---|---|
| `DataFlowEntityBinding.carrier_refs` | `DataCarrier` | binding привязывает сущности к данным; контейнеры не допускаются |
| `SelectedEntity.carrier_refs` | `DataCarrier` | то же |
| Форма коллекции | Variant B (раздельные) | спайк: gen-pydantic схлопывает полиморфный list в `TechnicalAsset` |
| `realizes_refs` | не хранить | источник истины — `Mapping` |
| `element_id` | сохранить `dams:physical/...` | стабильные ссылки; отклонение зафиксировано в ADR-032 |
| Родители database/schema | миграция не создаёт | XLSX-импорт создаёт `DataContainer` при наличии в источнике (ADR-033) |
| `integrity_digest` | пересчёт только demo | иначе нарушается неизменяемость ревизии |

## Transitional

Активы с эвристическим `asset_namespace` и бывшие `payload`/`message` помечены тегом `transitional` (+ `namespace_heuristic` где применимо). Список — в `docs/migration/reports/*-migration-report.md`.

## Негативные тесты

`packages/specification-dams/tests/test_technical_asset_checks.py`: цикл `parent_ref`; дубликат ключа; operation без `interface_ref`; `in_memory`+`location_uri`; недопустимый `asset_kind`; неверные концы `entity_physical`; `carrier_refs` на контейнер; `direction` на `DataContainer`.

Residue: `tests/architecture/test_no_physical_object_residue.py`.

## Проверенные команды

| Команда | Результат |
|---|---|
| `scripts/validate-schemas.ps1` | OK (lint warnings на слотах без description — без роста) |
| `scripts/validate-examples.ps1` | OK |
| `scripts/validate-requirements.ps1` | OK |
| `scripts/generate-contracts.ps1` | OK |
| `scripts/generate-artifacts.ps1` | OK |
| `scripts/compare-golden.ps1` | OK (после rebuild bundle) |
| architecture-check | OK |
| pytest specification-dams + standard-linkml + drawdb-adapter | 205 passed |
| pytest migration + residue + contracts | 6 passed |

## ADR

- ADR-031 (registry, Variant B) — Accepted  
- ADR-032 (identity) — Accepted  
- ADR-033 (quantum boundary, Kafka example, XLSX parents) — Accepted  

Спайк: `docs/migration/technical-asset-spike-report.md`.  
Инвентаризация: `docs/migration/technical-asset-inventory.md`.  
Changelog: `docs/migration/CHANGELOG-technical-asset.md`.
