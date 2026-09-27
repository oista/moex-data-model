# MOEX Workbench Plan

**Статус:** Draft  
**Версия:** 0.1  
**Целевая версия приложения:** MVP 0.1

> **Верхний канон архитектуры платформы:** [docs/architecture/MODELING_ARCHITECTURE.md](architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2). Этот план ориентирован на Workbench MVP; деревья вроде `apps/web` и `model-core` ниже — исторический/Workbench-контур и не отменяют modeling kernel (`ModelingStandard` / `ReferenceSpecification` / `SpecificationImplementation`).

## Исходное состояние

В текущем репозитории (https://github.com/oista/moex-data-model) уже присутствуют:

- Документ MOEX Data Model Specification.
- Набор LinkML schemas.
- Примеры экземпляров модели.
- Сгенерированные артефакты.
- Цветная DBML-проекция для drawDB.
- Каталог документации.

Это достаточная основа для начала приложения. Первой задачей должна стать не переработка метамодели, а создание воспроизводимого build и conformance pipeline вокруг существующих файлов.

## Целевая структура

```text
moex-data-model/
├── apps/
│   ├── api/
│   │   ├── src/moex_workbench/
│   │   └── tests/
│   ├── web/
│   │   ├── src/
│   │   └── tests/
│   └── drawdb/
│       ├── upstream/
│       └── moex-adapter/
├── packages/
│   ├── model-core/
│   │   └── src/moex_model/
│   ├── model-graph/
│   │   └── src/moex_model_graph/
│   ├── drawdb-adapter/
│   │   └── src/moex_drawdb/
│   ├── git-provider/
│   └── integration-adapters/
├── schemas/
│   ├── dams/
│   ├── profiles/
│   ├── policies/
│   └── imports/
├── models/
│   ├── corporate/
│   └── solutions/
├── mappings/
│   ├── eam/
│   ├── clinkr/
│   ├── catalog/
│   └── migrations/
├── examples/
├── tests/
│   ├── conformance/
│   ├── golden/
│   ├── compatibility/
│   └── integration/
├── generated/
│   └── .gitkeep
├── docs/
│   ├── architecture/
│   │   ├── MODELING_ARCHITECTURE.md   # normative platform canon
│   │   └── …
│   ├── IMPLEMENTATION_PLAN.md
│   └── adr/
├── infra/
│   ├── docker/
│   ├── compose/
│   └── helm/
├── pyproject.toml
├── uv.lock
├── package.json
├── Makefile
└── README.md
```

Миграция `model_src/` → `model-assets/` (+ `viewer/` → `apps/viewer`) выполнена: см. [docs/migration/model-src-to-model-assets.md](migration/model-src-to-model-assets.md). Целевое дерево Workbench ниже (`apps/web`, `model-core`) по-прежнему подчинено [MODELING_ARCHITECTURE.md](architecture/MODELING_ARCHITECTURE.md).

## Пакеты LinkML

### Обязательное ядро

| Компонент | Пакет или команда | Решение |
|---|---|---|
| LinkML toolchain | `linkml` | Обязательная dependency compiler/worker |
| Runtime API | `linkml-runtime` | Обязательная runtime dependency |
| LinkML metamodel | `linkml-model` | Транзитивная/зафиксированная dependency, не отдельное прикладное ядро |
| Проверка схем | `linkml validate` или `linkml-validate` | Обязательный CI gate |
| Проверка данных | `linkml validate -s` | Обязательный CI/API gate |
| Качество схем | `linkml-lint` | Обязательный CI gate |
| JSON Schema | `gen-json-schema` | Обязательно для frontend и API |
| Pydantic | `gen-pydantic` | Основной generated DTO |
| Python dataclasses | `gen-python` | Reference/conformance, не второй API model |
| Документация | `gen-doc` | Обязательный release artifact |
| Диаграммы | `gen-mermaid-class-diagram` | Документация |
| DBML | `gen-dbml` | Базовая генерация для drawDB |
| RDF | `gen-rdf` | Semantic export |
| OWL | `gen-owl` | Ontology export |
| SHACL | `gen-shacl` | RDF validation shapes |

LinkML официально предоставляет generators для JSON Schema, программных object models, RDF/OWL/SHACL и документации. Техническую документацию классов, slots и enums можно автоматически получать через `gen-doc`.

### Отдельные расширения

| Пакет | Статус в архитектуре | Применение |
|---|---|---|
| `linkml-map` | Optional controlled dependency | Mappings и migrations |
| `schema-automator` | Optional import dependency | Bootstrapping внешних схем |
| `linkml-owl` | Optional ontology dependency | LinkML instances → OWL |
| `linkml-store` | Experimental adapter | Исследование query/storage abstractions |
| `rdflib` | Ontology runtime | Чтение, запись и запрос RDF |
| `pyshacl` | Ontology validation | Проверка RDF instances |

### Решение по linkml-store

`linkml-store` не следует использовать как основную production database abstraction в MVP.

Причины:

- Не требуется для компиляции LinkML.
- Не должно скрывать транзакционные и security-возможности PostgreSQL.
- Создаёт лишний слой между приложением и operational schema.
- Его можно независимо проверить на задачах поиска по моделям, DuckDB analytics и portable collections.

Для него создаётся spike с интерфейсом:

```python
class ModelIndexProvider(Protocol):
    def index_revision(self, revision: ModelRevision) -> None: ...
    def search(self, query: ModelSearchQuery) -> list[ModelHit]: ...
```

Default implementation — PostgreSQL. `LinkMLStoreIndexProvider` включается feature flag.

### Решение по Python-моделям

Нельзя одновременно использовать generated Pydantic и generated dataclasses как два независимых источника runtime semantics.

Рекомендуется:

- `gen-pydantic` — API DTO, формы, request/response.
- `gen-python` — conformance и операции, где требуется `linkml-runtime`.
- `linkml-validate` — обязательный канонический validator.
- Custom semantic rules — отдельный слой.
- JSON Schema/AJV — предварительная browser validation.

Pydantic generator удобен для FastAPI, но generated Pydantic classes не должны подменять проверку всех LinkML constructs.

## Прикладные backend-пакеты

### API

```toml
fastapi
uvicorn
pydantic
pydantic-settings
python-multipart
orjson
httpx
```

### Persistence

```toml
sqlalchemy
alembic
psycopg[binary,pool]
```

### Background processing

```toml
celery
redis
```

В production broker выбирается после проверки корпоративных стандартов. Если утверждён RabbitMQ, Redis остаётся только cache/dev backend.

### Git

```toml
gitpython
httpx
```

`GitPython` используется для локальных checkout/worktree. Git provider APIs вызываются через `httpx`, чтобы не связывать доменную модель с конкретным Git hosting SDK.

### RDF и ontology

```toml
rdflib
pyshacl
linkml-owl
```

`linkml-owl` устанавливается только в ontology worker image либо optional dependency group.

### Parsing и utility

```toml
ruamel-yaml
jsonpatch
jsonpointer
deepdiff
semver
structlog
tenacity
```

`ruamel-yaml` необходим для аккуратного изменения YAML с сохранением порядка и комментариев. `jsonpatch` применяется не к исходному YAML напрямую, а к нормализованному representation с последующей безопасной сериализацией.

### Наблюдаемость

```toml
opentelemetry-api
opentelemetry-sdk
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-sqlalchemy
prometheus-client
```

### Тестирование

```toml
pytest
pytest-asyncio
pytest-cov
hypothesis
testcontainers
respx
syrupy
```

`Hypothesis` используется для генеративных тестов ModelGraph и round-trip. `syrupy` либо обычные golden files — для generated outputs.

### Quality

```toml
ruff
mypy
bandit
pip-audit
pre-commit
```

## Frontend-пакеты

Основной Workbench:

```text
React
TypeScript
Vite
React Router
TanStack Query
Zustand
React Hook Form
AJV
Monaco Editor
i18next
OpenAPI generated client
Vitest
Testing Library
Playwright
```

Назначение:

| Пакет | Роль |
|---|---|
| React | Application shell и формы |
| TanStack Query | Server state и jobs polling |
| Zustand | Локальный editor/workspace state |
| AJV | Проверка данных по generated JSON Schema |
| Monaco | LinkML YAML и mapping editor |
| React Hook Form | Governance и metadata forms |
| i18next | Русский и английский интерфейс |
| Playwright | End-to-end testing |

drawDB остаётся отдельным frontend build. Его внутренние зависимости не должны импортироваться в Workbench напрямую.

## Управление версиями

Вместо ручных диапазонов dependencies применяется:

```text
pyproject.toml → uv.lock
package.json → package-lock.json или pnpm-lock.yaml
```

Правила:

- Python minor version фиксируется для CI и production image.
- LinkML ecosystem фиксируется точными версиями в lockfile.
- Обновления выполняются отдельным dependency PR.
- В PR запускается полная golden/conformance matrix.
- Generated artifacts сравниваются с baseline.
- Изменение output без объяснения блокирует merge.
- Версии генераторов записываются в artifact manifest.

Пример manifest:

```yaml
artifact:
  model_id: moex:dams
  model_version: 0.1.0
  model_revision: 4f38c7...
  type: json-schema
  generator: gen-json-schema
  generator_version: pinned-by-lock
  configuration_digest: sha256:...
  artifact_digest: sha256:...
```

## Этап 0. Проверка основы

### Задачи

- Зафиксировать supported Python и Node versions.
- Создать `pyproject.toml` и lockfile.
- Зафиксировать LinkML ecosystem compatibility matrix.
- Установить `.linkmllint.yaml`.
- Проверить все существующие schemas.
- Проверить все examples.
- Повторно сгенерировать существующие artifacts.
- Сравнить результаты с файлами в `generated/`.
- Проверить лицензии LinkML ecosystem и drawDB.
- Зафиксировать ADR-001–ADR-012 (проекты: [docs/adr/](adr/README.md); приёмка = Proposed → Accepted).
- Создать baseline CI.
- **Target-after-slice layout:** миграция `model_src/` → `model-assets/`, `viewer/` → `apps/viewer`, конверты активов (сделано; см. [migration](migration/model-src-to-model-assets.md)). `make check` включает slice + architecture-check + lint/validate схем.
- **Roadmap phases 1–4 (2026-09-28):** (1) `make generate-contracts` → `moex_dams_contracts`; (2) `OWLStandardProvider`; (3) `packages/git-adapter` + CLI lint/compile/diagram/diff; (4) `apps/api` FastAPI + Alembic core tables + `infra/compose/postgres.yml` (SQLite smoke / Postgres compose).
- **Stage 3 narrow-v2 (2026-09-28):** Alembic `0002` — `user_identity`, `role_binding`, `workspace_member`, `generation_job`, `generated_artifact`, `model_index`, `model_element_index`; ports `IdentityStore` / `JobStore` / `ModelIndexProvider`; HTTP workspaces + sync jobs (Idempotency-Key) + model-index rebuild/search; GitHub read-only `GitProvider` via `MOEX_GIT_PROVIDER`. Still out: OIDC, RLS, `diagram_layout`, `publication_request`, async workers.

### Результат

Команда:

```bash
make check
```

должна выполнять:

```text
validate-schemas
lint-schemas
validate-examples
test-semantic-rules
generate
compare-golden
test-python
```

### Критерии готовности

- Все схемы загружаются.
- Все imports разрешаются без обращения к непроверенным URL.
- Все examples проходят validation.
- Все generated outputs воспроизводимы.
- Нет ручных изменений generated files.
- CI работает на чистом checkout.

## Этап 1. Model Core

### Задачи

- Создать `SchemaRepository`.
- Создать `SchemaLoader`.
- Создать `ModelInstanceLoader`.
- Реализовать `ModelGraph`.
- Реализовать преобразование LinkML → ModelGraph.
- Реализовать ModelGraph → JSON API DTO.
- Реализовать индекс элементов.
- Реализовать разрешение CURIE и URI.
- Реализовать semantic validation framework.
- Подключить существующие MOEX-инварианты.
- Реализовать единый формат diagnostics.

Diagnostic:

```json
{
  "code": "MOEX-MAPPING-001",
  "severity": "error",
  "message": "Mapping must have at least one source and target",
  "path": "mappings[3]",
  "element_id": "moex:mapping:123",
  "source": "model.yaml",
  "line": 241,
  "suggestion": "Add source_element_refs and target_element_refs"
}
```

### Критерии готовности

- ModelGraph строится для всей DAMS.
- Идентификаторы не зависят от имени файла.
- Ошибки имеют stable code.
- API не возвращает internal LinkML runtime objects.
- Unit coverage критических модулей не ниже согласованного порога.

## Этап 2. Compiler CLI

До web-приложения необходимо сделать стабильный CLI.

### Команды

```text
moex-model validate
moex-model lint
moex-model compile
moex-model diff
moex-model import
moex-model map
moex-model diagram
moex-model publish
```

Примеры:

```bash
moex-model validate models/solutions/trading/model.yaml
moex-model compile models/solutions/trading/model.yaml --target all
moex-model diff --from v0.1.0 --to HEAD
moex-model diagram model.yaml --profile logical --format dbml
```

### Критерии готовности

- CLI и API вызывают один application layer.
- CLI возвращает стабильные exit codes.
- Каждый generated artifact имеет manifest.
- Повторная генерация идентична побайтно либо отличается только явно разрешёнными полями.

## Этап 3. API и persistence

**Progress (narrow-v2):** FastAPI + Alembic core/`0002`, ports + SQL adapters, workspace/job/index APIs, Idempotency-Key, DevAuth, GitHub **read-only** provider. Remaining: OIDC, domain authz/RLS, `diagram_layout`, `external_registry_cache`, `publication_request`, async workers, write GitHub.

### Задачи

- Создать FastAPI application.
- Ввести repository interfaces.
- Создать PostgreSQL operational schema.
- Добавить Alembic migrations.
- Реализовать workspace lifecycle.
- Реализовать job API.
- Реализовать artifact registry.
- Реализовать audit log.
- Добавить OIDC authentication.
- Реализовать domain-based authorization.
- Реализовать GitHub provider первой версии.
- Добавить idempotency keys для write operations.

### Таблицы MVP

```text
user_identity
role_binding
workspace
workspace_member
model_index
model_element_index
model_revision_index
diagram_layout
validation_run
validation_diagnostic
generation_job
generated_artifact
external_registry_cache
publication_request
audit_event
```

### Критерии готовности

- API поднимается без frontend.
- OpenAPI проходит validation.
- Все write endpoints защищены.
- Повторный submit с одним idempotency key не создаёт вторую операцию.
- Workspace изолирован от других пользователей.
- Публикация записывает audit trail.

## Этап 4. Web Workbench

**Progress (MVP shell + editors):** `apps/web` React + Vite + TanStack Query поверх `apps/api` — dashboard, workspaces, model registry, trading conformance + model-index search, validate job report, DevAuth actor bar; Monaco YAML editor + `workspace_document` draft + `source=draft` validate. Out: entity/attribute forms, form↔YAML sync, semantic diff, publication/PR, drawDB, OIDC, i18n.

### Основные экраны

- Dashboard.
- Реестр моделей.
- Страница модели.
- Model explorer.
- LinkML YAML editor.
- Entity editor.
- Attribute editor.
- Relationship editor.
- Mapping editor.
- Validation report.
- Semantic diff.
- Artifact preview/download.
- Publication review.
- Administration of external registry connections.

### Поведение редактора

- Monaco получает LinkML metamodel JSON Schema.
- Ошибки YAML отображаются сразу.
- Полная LinkML validation выполняется backend.
- Форма и YAML синхронизируются через controlled patch.
- Несохранённые изменения остаются в workspace.
- Пользователь видит base revision и возможный конфликт.

### Критерии готовности

- Можно открыть существующую модель.
- Можно добавить LogicalEntity и LogicalAttribute.
- Можно проверить workspace.
- Можно просмотреть semantic diff.
- Можно сформировать PR без ручной работы в Git.

## Этап 5. drawDB MVP

### Задачи

- Зафиксировать upstream revision drawDB.
- Создать отдельный image.
- Реализовать безопасный embedding.
- Создать `DrawDbProjectionService`.
- Преобразовать ModelGraph в DBML.
- Добавить MOEX colors.
- Добавить фильтрацию слоёв.
- Хранить diagram layout отдельно.
- Получать изменённый DBML.
- Вычислять `ModelPatch`.
- Показывать preview semantic diff.
- Запрещать неразрешённые изменения.
- Добавить golden round-trip tests.

### Первый scope

Поддержать редактирование:

- LogicalEntity.
- LogicalAttribute.
- Relationship.
- PhysicalObject типа table/view.
- PhysicalField.
- Physical foreign keys.
- Description.
- Required/nullability.
- Logical/native type mapping.

Не поддерживать:

- Mapping expressions.
- Ownership.
- Classification.
- DataFlow topology.
- Analytics profile.
- LinkML mixins.
- LinkML rules.
- Abstract class semantics.

### Round-trip test

```text
LinkML A
  → ModelGraph A
  → DBML A
  → DBML parser
  → ModelGraph B
  → LinkML patch
```

Успешный результат:

- Ни один element ID не потерян.
- Отсутствующий в DBML semantic metadata не удалён.
- Неизменённые элементы не попали в patch.
- Изменённые properties отражены в semantic diff.
- Patch проходит полную validation.
- Повторная проекция стабильна.

## Этап 6. Generators

### Обязательные pipelines

```text
linkml → JSON Schema
linkml → Pydantic
linkml → Python
linkml → Markdown docs
linkml → Mermaid
linkml → DBML
linkml → RDF
linkml → OWL
linkml → SHACL
```

### Проверки

- JSON Schema проходит metaschema validation.
- Generated Python компилируется.
- Generated Pydantic импортируется.
- RDF парсится rdflib.
- OWL Turtle парсится rdflib.
- SHACL shapes парсятся и проходят test fixtures.
- DBML импортируется выбранной версией drawDB.
- Generated docs не содержат broken internal links.

### Критерии готовности

- Pipeline вызывается через API и CLI.
- Невалидный output блокирует публикацию.
- Generator options версионируются.
- Все outputs доступны как единый release bundle.

## Этап 7. Mapping и импорт

### LinkML Map

Реализовать:

- Хранилище transformation specifications.
- Validation mappings.
- Preview transformation.
- Sample-based execution.
- Migration mappings между версиями DAMS.
- Audit source/target schema revisions.
- Запрет unrestricted evaluation по умолчанию.
- Allowlist функций expressions.

### Schema Automator

Реализовать import wizard:

1. Пользователь загружает JSON Schema, SQL, CSV/TSV или RDF/OWL.
2. Система запускает isolated import job.
3. Создаётся inferred LinkML schema.
4. Пользователь выбирает target profile.
5. Система показывает diagnostics и uncertainty.
6. Результат сохраняется как draft.
7. Архитектор обогащает IDs, descriptions, ranges и registry links.
8. Только после validation draft может стать model package.

### Критерии готовности

- Ни один импорт не публикуется автоматически.
- Исходный файл и параметры import job сохраняются.
- Mapping имеет source и target revision.
- Повторный импорт воспроизводим.
- Неоднозначности показаны пользователю.

## Этап 8. Ontology

### Задачи

- Зафиксировать URI policy.
- Зафиксировать prefix registry.
- Определить mapping enums в OWL.
- Определить обработку mixins.
- Генерировать RDF/OWL/SHACL.
- Проверять синтаксис.
- Добавить pySHACL fixtures.
- Добавить optional linkml-owl instance export.
- Добавить ontology profile report.

### Критерии готовности

- Каждый класс и slot имеет стабильный URI либо диагностическую ошибку.
- OWL output не используется для решения о валидности YAML instances.
- SHACL validation согласована с контрольными examples.
- Изменение URI считается breaking change.
- Ontology output связан с model revision.

## Этап 9. Интеграции MOEX

### Adapter interfaces

```python
class RegistryAdapter(Protocol):
    registry_type: str

    async def fetch_changed(self, cursor: str | None) -> RegistryPage: ...
    async def resolve(self, identifier: str) -> RegistryObject | None: ...
    async def health(self) -> HealthStatus: ...
```

### Реализации

- EAM adapter.
- Clinkr adapter.
- Data Catalog adapter.
- Business Glossary adapter.
- IAM organization/role adapter.
- Data Contract adapter.

### Правила

- Внешний объект хранится как read-only projection.
- Всегда сохраняются external ID, source URI и last synchronized revision.
- Пользователь видит stale/unresolved references.
- Недоступность внешней системы не должна повреждать локальную модель.
- Публикация может блокироваться только policy-configured проверками.

## Этап 10. Совместимость

### Semantic diff

Классифицировать изменения:

| Изменение | Категория |
|---|---|
| Добавление optional slot | Backward-compatible |
| Удаление slot | Breaking |
| Optional → required | Breaking |
| Расширение enum | Зависит от compatibility mode |
| Удаление enum value | Breaking |
| Изменение identifier | Breaking |
| Изменение URI | Breaking |
| Уточнение description | Non-breaking |
| Усиление классификации | Governance-impacting |
| Изменение physical mapping | Operational-impacting |

### Migration support

Для breaking changes должны поддерживаться:

- Migration note.
- LinkML Map transformation.
- Compatibility baseline.
- Список затронутых contracts.
- Список затронутых integrations.
- Approval decision.

## Этап 11. Production hardening

### Требования

- Horizontal scaling API и workers.
- Backup/restore Postgres.
- Artifact retention policy.
- Git provider failover procedure.
- Queue retry и dead-letter handling.
- Request и job limits.
- Antivirus integration.
- Secrets from secret manager.
- Network policies.
- Security test.
- Disaster recovery exercise.
- Performance baseline.
- Audit export.
- Руководства администратора и пользователя.

## CI/CD

### Pull request pipeline

```text
1. Validate YAML
2. Validate LinkML schemas
3. Run linkml-lint
4. Validate examples
5. Run MOEX semantic rules
6. Run unit tests
7. Generate artifacts
8. Compare golden files
9. Compile generated Python
10. Parse RDF/OWL/SHACL
11. Validate DBML projection
12. Run frontend tests
13. Run security scans
14. Build OCI images
```

### Release pipeline

```text
1. Verify approved PR
2. Merge to protected branch
3. Build immutable source bundle
4. Generate all artifacts
5. Produce manifest and checksums
6. Tag Git revision
7. Publish OCI images
8. Publish model bundle
9. Update model registry projection
10. Write audit event
```

## Стратегия тестирования

| Уровень | Что проверяется |
|---|---|
| Unit | Parsers, ModelGraph, rules, converters |
| Golden | Стабильность generated outputs |
| Property-based | Round-trip и случайные комбинации entities/slots |
| Conformance | Официальные и MOEX LinkML fixtures |
| Integration | PostgreSQL, Git, broker, artifact storage |
| Contract | EAM, Clinkr, catalog adapters |
| E2E | Workspace → edit → validate → PR |
| Security | Authorization, imports, expressions, uploads |
| Performance | Большие schemas и model packages |

## Начальные epics

### EPIC-01 Repository foundation

- Перенести `model_src` → `model-assets/` (сделано; см. docs/migration/).
- Добавить build.
- Добавить lockfiles.
- Добавить validation pipeline.
- Зафиксировать golden artifacts.

### EPIC-02 ModelGraph

- LinkML loader.
- Internal graph.
- Semantic rules.
- Diagnostics.
- Semantic diff.

### EPIC-03 Compiler

- CLI.
- Generator registry.
- Artifact manifests.
- Reproducible output.

### EPIC-04 Backend

- FastAPI.
- PostgreSQL.
- Workspaces.
- Jobs.
- Git provider.
- OIDC.

### EPIC-05 Frontend

- Model registry.
- Explorer.
- Monaco.
- Forms.
- Validation report.
- Diff viewer.

### EPIC-06 drawDB

- Self-hosted build.
- DBML projection.
- Import DBML.
- Patch preview.
- Round-trip tests.

### EPIC-07 Semantic ecosystem

- LinkML Map.
- Schema Automator.
- RDF/OWL/SHACL.
- Registry adapters.

## Первые четыре итерации

### Итерация 1

- Repository restructure.
- `pyproject.toml`.
- Lockfile.
- Make targets.
- Schema validation.
- Linter.
- Example validation.
- Golden generation.
- Architecture ADRs.

### Итерация 2

- ModelGraph.
- Unified diagnostics.
- Semantic rules.
- CLI `validate`.
- CLI `compile`.
- Semantic diff prototype.

### Итерация 3

- FastAPI skeleton.
- PostgreSQL migrations.
- Model registry.
- Workspaces.
- Job framework.
- Git read integration.

### Итерация 4

- React shell.
- Model explorer.
- Monaco LinkML editor.
- Validation UI.
- DBML generation.
- Embedded drawDB read-only preview.

Двустороннее редактирование drawDB следует начинать только после стабилизации ModelGraph и semantic diff.

## Риски

| Риск | Мера |
|---|---|
| Потеря LinkML semantics при DBML round-trip | Ограниченный профиль и patch-based update |
| Нестабильность LinkML Map | Provider interface, pinned version, conformance tests |
| Ошибки schema-automator | Только draft import и ручное подтверждение |
| Расхождение Pydantic и LinkML validation | Канонический `linkml-validate` |
| Дублирование Git и PostgreSQL | Git — published source, DB — operational projection |
| Изменение output при обновлении LinkML | Lockfile и golden tests |
| Произвольное выполнение mapping expressions | Restricted execution и isolation |
| Vendor lock-in GitHub | GitProvider interface |
| Зависимость от внутреннего drawDB JSON | Интеграция через DBML и adapter |
| Большие модели перегружают canvas | Фильтры и diagram projections |
| Несогласованные URI | Централизованная URI policy и lint rules |

## Правила для Claude Code

Claude должен выполнять план следующими независимыми pull requests:

1. Не изменять семантику существующей метамодели без отдельного ADR.
2. Не редактировать `generated/` вручную.
3. Перед изменением LinkML проверять существующие examples.
4. После изменения запускать полную генерацию.
5. Любое изменение golden output объяснять в PR.
6. Не добавлять framework без записи в dependency decision table.
7. Не связывать domain layer с FastAPI, SQLAlchemy, GitHub или drawDB DTO.
8. Использовать interfaces в domain/application layer.
9. Для каждого endpoint добавлять authorization test.
10. Для каждого converter добавлять positive, negative и round-trip fixture.
11. Не включать unrestricted mapping evaluation.
12. Не использовать `linkml-store` как primary persistence.
13. Не делать DBML канонической моделью.
14. Не удалять неизвестные LinkML annotations при визуальном редактировании.
15. Каждый PR должен быть запускаем на чистом checkout одной документированной командой.

## Definition of Done MVP

MVP завершён, если пользователь может:

1. Войти через OIDC.
2. Найти модель IT-решения.
3. Создать workspace от выбранной Git revision.
4. Открыть LinkML YAML и структурированное представление.
5. Увидеть logical/physical diagram в drawDB.
6. Добавить сущность, атрибут и relationship.
7. Получить LinkML, lint и MOEX diagnostics.
8. Сформировать semantic diff.
9. Сгенерировать JSON Schema, Pydantic, DBML, RDF, OWL, SHACL и документацию.
10. Создать pull request.
11. После merge открыть опубликованную immutable revision.
12. Скачать воспроизводимый artifact bundle с manifest и checksums.

Критический порядок реализации: сначала build и validation, затем ModelGraph и semantic diff, потом API/UI, и только после этого двусторонний drawDB. Это не позволит превратить визуальный редактор в альтернативный и несовместимый источник модели.
