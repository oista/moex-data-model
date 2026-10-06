# DataStructure / SchemaNode — отчёт было → стало

Schema DAMS: **1.0.0 → 2.0.0** (путь `0.1/` сохранён). Окно deprecation 1.1.0 пройдено в той же ветке до удаления `PhysicalField`.

## Было → стало

| Было | Стало |
|------|--------|
| `PhysicalField` на `DataCarrier.physical_fields` | `DataStructure.nodes` (плоский список `SchemaNode`) + `root_local_key` |
| `HasStructure.structure_ref` / opaque URI | `structure_ref` → `DataStructure`; старый URI → `source_artifact_ref` |
| `schema_path` / dotted path | промежуточные `object`-узлы + рёбра `children` (`local_key`) |
| Mapping / selections на поля | CURIE `structure_id#local_key` (ADR-039) |
| `asset_kind: message_type` / transitional | класс `Message` + `payload_structure_ref` / `headers_structure_ref`; `AccessPoint.message_refs` |
| `schema_dialect` на `HasStructure` | снят с миксина; опциональный `schema_dialect` на `DataStructure` (версия формата схемы) |
| Типы полей ad-hoc | существующие `DataType` / `NativeTypeBinding` (этап 6 ТЗ не дублировался) |

## Миграция инстансов

Скрипт: `scripts/migrate_physical_field_to_schema_node.py`.  
Отчёт прогона: `docs/migration/physical-field-migration-report.md`.

| Решение | fields → scalar nodes | structures | mapping rewrites |
|---------|----------------------:|-----------:|-----------------:|
| mdm | 42 | 4 | 42 |
| crm | 58 | 3 | 58 |
| esed | 68 | 12 | 68 |
| ucd | 39 | 7 | 40 |
| **итого live** | **207** | **26** | — |

(+ examples / draft imports). Коллизий `local_key` при миграции не зафиксировано. Неоднозначных Message-каналов нет (messages_created=0 на live-решениях). Непрозрачные старые `structure_ref` перенесены в `source_artifact_ref` (список в migration-report).

## Негативы / конформанс

- Реляционные признаки (`is_primary_key` / FK / …) **только** при `schema_format=relational` — проверка в DAMS (`data_structure.py`), не в `linkml-validate`.
- Фикстуры: 4 позитивные + негативы из ТЗ; PDM-* в `it-solution-requirements.yaml`.
- Residue: `tests/architecture/test_no_physical_field_residue.py` (allowlist: migrate script, changelog, ADR, inventory, `tmp/`).

## Спайк генераторов

`docs/migration/data-structure-spike-report.md` + ADR-038: выбрана **плоская** форма (`nodes` + `root_local_key`). Inlined-дерево отвергнуто (diff/SQL/CURIE).

## Golden / артефакты

- `make generate-contracts` / `generate-artifacts` / `build_release_bundle` — обновлены.
- `compare-golden OK` (contracts, json-schema, owl, shacl, dbml, mermaid, python, doc, rdf, ontology-profile, bundle).
- Notes: `docs/migration/golden-diff-data-structure.md`.
- Bundle digest: `sha256:601156ebb48f8e23270dbbf9486bc9b76b9c66da447026d29db79ff7038caccd`.

## Временные решения (долг)

- `Message` в `moex-structure.yaml` из‑за цикла импорта core↔integration (ADR-040).
- String-диалекты / стартовый enum `SchemaFormatEnum`; перенос в реестр — отдельно.
- `constraint_expressions` без `Expression`.

## Проверки

```
check_all OK
  generate-contracts, slice-cli, validate-schemas, validate-examples,
  validate-requirements, compare-golden, architecture-check, publish-gate
```

ADR-038…041: **Accepted**. Changelog: `docs/migration/CHANGELOG-data-structure.md`.
