# MOEX Data Model

Платформа управления формальными модельными активами MOEX: стандарты моделирования, нормативные спецификации и конкретные реализации моделей.

## Архитектурная идея

Система строится вокруг трёх ролей (не «типов файлов»):

| Роль | Смысл | Пример сейчас |
|---|---|---|
| **ModelingStandard** | формализм | LinkML |
| **ReferenceSpecification** | норма / профиль на стандарте | MOEX DAMS 0.1 |
| **SpecificationImplementation** | конкретная версионированная модель | trading-solution |

Нормативный документ: [`docs/architecture/MODELING_ARCHITECTURE.md`](docs/architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2).  
Схема ядра: [`docs/architecture/modeling-kernel.yaml`](docs/architecture/modeling-kernel.yaml).  
Чеклист ревью docs/architecture: [`docs/architecture/CHECKLIST.md`](docs/architecture/CHECKLIST.md).

Workbench / LinkML toolchain описаны отдельно в [`docs/architecture/linkml_architecture.md`](docs/architecture/linkml_architecture.md) — это **не** верхний уровень архитектуры. Целевая раскладка пакетов после вертикального среза — [`docs/architecture/app_model.md`](docs/architecture/app_model.md) (`target-after-slice`).

```text
LinkML (standard)
  → MOEX DAMS 0.1 (specification, tree_root: MOEXModelRepository)
      → solution ModelPackage (implementation)
          → conformance → publication viewer
```

Publication viewer, HTML, search index, drawDB и будущий Workbench — **производные** над ядром, не source of truth.

## Что уже есть в репозитории

| Путь | Роль сегодня |
|---|---|
| [`model_src/`](model_src/) | DAMS schemas + examples (временный путь до миграции в `model-assets/`) |
| [`viewer/`](viewer/) | статический Publication Viewer (`publish.yaml` → `viewer/dist`) |
| [`packages/modeling-kernel/`](packages/modeling-kernel/) | envelopes + `StandardProvider` (TSpecBody ≠ TImplBody) |
| [`packages/standard-linkml/`](packages/standard-linkml/) | LinkML provider + ER-dictionary ingest |
| [`packages/specification-dams/`](packages/specification-dams/) | DAMS semantic rules, graph view, conformance |
| [`packages/publication/`](packages/publication/) | slice → PublicationModule / viewer JSON |
| [`apps/cli/`](apps/cli/) | inbound CLI `moex-model` (`validate` / `publish`) |
| [`packages/ontology/`](packages/ontology/) | FIBO CSV shim над [`packages/standard-owl/`](packages/standard-owl/) |
| [`tools/architecture-check/`](tools/architecture-check/) | механические проверки architecture pack |
| [`docs/architecture/`](docs/architecture/) | нормативная архитектура и связанные черновики |
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | план Workbench MVP (подчинён MODELING_ARCHITECTURE) |

Физический перенос `model_src/` → `model-assets/` и корневого `viewer/` → `apps/viewer` — **после** стабилизации среза. Первый inbound adapter уже в [`apps/cli/`](apps/cli/).

## Быстрый старт

Нужен Python **3.11+** (на Windows часто удобнее `py -3.14`, если `python` указывает на 3.10).

### Publication Viewer

```bash
# из корня репозитория
py -3.14 -m pip install -e "./viewer[dev]"
py -3.14 -m moex_publication_viewer.cli build --root .
# открыть viewer/dist/index.html
```

Или `make viewer` / `make viewer-check` (если установлен `make`; можно задать `PYTHON=py -3.14`).

Новый раздел публикации: добавить `publish.yaml` рядом с источниками — без правок UI. Подробности: [`viewer/README.md`](viewer/README.md).

### Проверка architecture pack

```bash
py -3.14 -m pip install -e "./tools/architecture-check[dev]"
py -3.14 -m pytest tools/architecture-check/tests -q
py -3.14 -m architecture_check.cli --root .
```

Или `make architecture-check`. Ловит, в частности:

- provider-specific классы (`LinkML*`, …) в `modeling-kernel.yaml` при `extension_policy`;
- ровно один `normative: true` в `docs/architecture/*.md`;
- согласованность DAMS `tree_root` (`MOEXModelRepository`) с нормативным текстом.

### DAMS schemas

```bash
pip install linkml
cd model_src/schemas
linkml-lint moex-dams.yaml
```

Состав схем и примеры: [`model_src/README.md`](model_src/README.md).

### Первый вертикальный срез и CLI

```bash
make check
# или: powershell -NoProfile -File apps/cli/scripts/check.ps1
```

Прогоняет kernel / LinkML provider / DAMS assess / publication / CLI и пишет
[`model_src/examples/publications/vertical_slice.json`](model_src/examples/publications/vertical_slice.json)
через `moex-model publish`. Секции viewer — в [`model_src/examples/publish.yaml`](model_src/examples/publish.yaml).

```bash
py -3.14 -m moex_model_cli validate --root .
py -3.14 -m moex_model_cli publish --root .
```

Пакетный срез без CLI: `make vertical-slice-check`.

### FIBO glossary export (опционально)

См. [`packages/ontology/README.md`](packages/ontology/README.md). Viewer по умолчанию использует закоммиченный preview CSV, не полный mart.

## Документация

| Документ | Статус |
|---|---|
| [MODELING_ARCHITECTURE.md](docs/architecture/MODELING_ARCHITECTURE.md) | **normative** — ядро платформы |
| [modeling-kernel.yaml](docs/architecture/modeling-kernel.yaml) | схема modeling kernel |
| [app_model.md](docs/architecture/app_model.md) | Draft — целевое дерево пакетов |
| [linkml_architecture.md](docs/architecture/linkml_architecture.md) | Draft — Workbench / LinkML toolchain |
| [CHECKLIST.md](docs/architecture/CHECKLIST.md) | process gate для PR по architecture |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Draft — Workbench MVP roadmap |
| [MOEX Data Model Specification v0.1](docs/MOEX%20Data%20Model%20Specification%20v0.1%20на%20основе%20LinkML.md) | спецификация DAMS на LinkML |

## Именование

Метамодель и префикс — **DAMS** (`https://data.moex.com/dams/`, корневой файл `moex-dams.yaml`). Старый акроним MDMS не используется.

## Принципы (кратко)

1. Роли ≠ технологии: один формат может быть standard, specification или implementation.
2. Typed body стандарта живёт в provider schema, не в modeling kernel.
3. Specification body (schema) и implementation body (instance) — разные типы в API.
4. Git — реестр опубликованных активов; PostgreSQL/object storage — operational / derived.
5. Добавление нового стандарта не должно править classes kernel (`make architecture-check`).
