---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-003: PostgreSQL — операционное хранилище и поисковая проекция

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §11, §16  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «PostgreSQL»

## Context

Платформе нужны **две разные правды**, и их нельзя смешивать.

**Опубликованная модель** — это Git-ревизия YAML (ADR-002). Её можно прочитать, воспроизвести артефакты, сравнить в PR. Это канон.

**Работа над моделью** — это другое. Workbench должен помнить:

- кто вошёл и какие у него роли;
- в каком workspace пользователь правит черновик (ещё не merge);
- какие джобы генерации/валидации запущены и чем закончились;
- кто что менял (аудит);
- координаты фигур на диаграмме drawDB (layout не живёт в YAML модели);
- поисковый индекс: «найди сущность по имени / URI / слою» без обхода всего Git на каждый запрос.

Git для этого плох. Черновик в незакоммиченном файле не даёт транзакций, прав доступа по строкам, очереди джобов и полнотекстового поиска. Класть identity, audit и layout в тот же репозиторий, что и канон DAMS, смешает операционные данные с моделью.

Отдельно в экосистеме LinkML есть `linkml-store`: абстракция «коллекции документов» над DuckDB, Mongo, Postgres и т.п. Искушение — сделать его основной БД Workbench, чтобы «не писать SQL». Минусы: скрывает транзакции и security PostgreSQL (в том числе RLS), добавляет слой между приложением и своей схемой, не нужен для компиляции LinkML. Его место — эксперимент по поиску/portable collections, не production persistence.

На текущем вертикальном срезе (§13) PostgreSQL **нет**. Есть Git-файлы и пересобираемые проекции: JSON для viewer, SQLite для Ontology Catalog. Это нормально для read-only публикации. Workbench с черновиками, джобами и поиском без operational store не запустится.

## Decision

Когда появится persistence Workbench, роли хранилищ такие:

1. **Git** — канон опубликованных спецификаций и реализаций (ADR-002). PostgreSQL его не подменяет.
2. **PostgreSQL** — единственное default-хранилище **операционного состояния** и **поисковой проекции**:
   - пользователи, роли, workspace;
   - черновики и незавершённые правки до merge в Git;
   - состояние джобов;
   - аудит;
   - ссылки на PR;
   - кэш поискового индекса по опубликованным ревизиям;
   - layout диаграмм;
   - метаданные сгенерированных артефактов и отчёты валидации.
3. **Object storage** (S3-совместимое) — сами generated-файлы (ZIP, JSON Schema, DBML, RDF/OWL, HTML). В PostgreSQL — только метаданные и ключ объекта.
4. **`linkml-store`** — не основная production-абстракция БД. Допустим spike за `ModelIndexProvider` и feature flag (`LinkMLStoreIndexProvider`). Default реализации поиска — PostgreSQL.

Поисковый индекс — **проекция**: его можно снести и пересобрать из Git-ревизии. Черновик в PostgreSQL — ещё не публикация; публикация = merge/tag в Git + воспроизводимый bundle (ADR-011, ADR-012).

Домен и application не импортируют SQLAlchemy и драйвер Postgres напрямую (hexagon, инвариант 11): доступ через port (`WorkspaceStore`, `JobStore`, `ModelIndexProvider` и т.п.).

## Consequences

- Схема Postgres, Alembic, backup/restore и retention — этап production hardening, не срез §13.
- SQLite в первом инкременте Ontology Catalog — локальная пересобираемая проекция каталога, не отмена этого ADR для Workbench.
- Дублирование «модель в Git и что-то похожее в Postgres» ожидаемо: Git — published source, БД — operational + search. Расхождение лечится пересборкой индекса, а не «истиной в БД».
- RLS PostgreSQL можно использовать для изоляции workspace/доменов; это инфраструктурный адаптер, не правило ядра.

## Alternatives

| Вариант | Почему нет |
|---|---|
| `linkml-store` как основная БД | лишний слой; слабее контроль транзакций и security Postgres; не нужен для LinkML compile |
| Только Git, без БД | нет нормальных черновиков, джобов, аудита, поиска, layout |
| PostgreSQL как master опубликованных моделей | теряется PR/review, сложно доказать неизменяемость ревизии (см. ADR-002) |
| Neo4j / triplestore как operational DB | избыточно для users/jobs/audit; RDF — забота OWL/RDF provider, не ядра |
| Оставить SQLite навсегда и для Workbench | нет RLS, слабее конкурентный доступ и operational tooling |

## Related

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) — «Решение по linkml-store»
- ADR-002, ADR-004, ADR-011, ADR-012
