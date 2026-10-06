---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-039: Адресация узлов SchemaNode

**Date:** 2026-10-06  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-030](ADR-030-dams-uri-and-prefix-policy.md), [ADR-038](ADR-038-datastructure-and-schemanode.md)  
**Amends:** [ADR-030](ADR-030-dams-uri-and-prefix-policy.md)

## Context

Поля и узлы структуры не являются `ModelElement` с глобальным `element_id` (ADR-033, ADR-038). Mapping, selections и `foreign_key_target` нуждаются в стабильной ссылке на узел внутри `DataStructure`. Политика URI/prefix (ADR-030) покрывает schema IRIs и instance `element_id`, но не фрагментную адресацию встроенных узлов.

## Decision

### Форма CURIE

Адрес узла: **`structure_id#local_key`**, где:

- `structure_id` — CURIE / URI `DataStructure` (например `dams:structure/…`);
- `#local_key` — фрагмент с локальным ключом узла внутри этой структуры.

Range слотов Mapping / `schema_node_refs` / `foreign_key_target` — `uriorcurie` в этой форме.

### Алфавит `local_key`

Паттерн: `^[a-z0-9_.-]+$` (без `#`, `/`, пробелов и прочих символов). Задаётся в схеме (`pattern` на `local_key` / `root_local_key`) и проверяется DAMS при необходимости.

### Генерация ключа (миграция / ingest)

1. Lowercase slug сегментов пути; `.` — разделитель вложенности (`a.b.c`).
2. Запрещённые символы исходного имени → `_`.
3. Пустой slug → `_`.
4. **Коллизии:** суффикс `-2`, `-3`, …; каждая коллизия фиксируется в `migration-report.md`.
5. После записи в модель ключ **заморожен**.

### Заморозка и переименование

- Миграция один раз вычисляет ключ из `schema_path` / `native_name`.
- Дальше `local_key` **не** пересчитывается при смене `native_name`.
- Повторный запуск скрипта на уже мигрированной модели не меняет ключи (идемпотентность **по множеству ключей**, не только по счётчику).
- Ручная смена ключа — breaking для Mapping / selections.

### Версионирование структуры

Новая версия = новый `DataStructure` + `previous_version_ref`. Ключи в новой версии **независимы** от предыдущей (не требуется сохранять те же `local_key`).

### Поправка к ADR-030

Дополнить политику instance-адресов: фрагмент `#local_key` на CURIE `DataStructure` — канонический способ ссылаться на `SchemaNode`. Не вводить отдельный prefix и не назначать узлам глобальный `element_id`.

## Consequences

- Diff и SQL индексируют узлы по `(structure_id, local_key)`.
- Viewer показывает `native_name`, но навигация и Mapping держатся за `local_key`.
- Тесты миграции проверяют стабильность множества ключей при повторном прогоне.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Глобальный `element_id` на каждом SchemaNode | взрыв кардинальности; конфликтует с EmbeddedElement |
| Path-only адресация без заморозки | переименование ломает Mapping |
| Произвольный Unicode в `local_key` | ломает CURIE/фрагменты и SQL-идентификаторы |
| Сохранять те же ключи между версиями структуры | связывает версии жёстче, чем `previous_version_ref` |

## References

- ADR-030 (URI / prefix policy) — amends
- ADR-038 (DataStructure / SchemaNode)
- RFC 3986 — fragment identifier
