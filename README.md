# MOEX Data Model

Платформа управления формальными модельными активами MOEX: стандарты моделирования, нормативные спецификации и конкретные реализации моделей.

## Архитектурная идея

Система строится вокруг трёх ролей (не «типов файлов»):

| Роль | Смысл | Пример сейчас |
|---|---|---|
| **ModelingStandard** | формализм | LinkML |
| **ReferenceSpecification** | норма / профиль на стандарте | MOEX DAMS 0.1 |
| **SpecificationImplementation** | конкретная версионированная модель | mdm |

Нормативный документ: [`docs/architecture/MODELING_ARCHITECTURE.md`](docs/architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2).  
Схема ядра: [`docs/architecture/modeling-kernel.yaml`](docs/architecture/modeling-kernel.yaml).  
Чеклист ревью docs/architecture: [`docs/architecture/CHECKLIST.md`](docs/architecture/CHECKLIST.md).

Workbench / LinkML toolchain описаны отдельно в [`docs/architecture/linkml_architecture.md`](docs/architecture/linkml_architecture.md) — это **не** верхний уровень архитектуры. Целевая раскладка пакетов — [`docs/architecture/app_model.md`](docs/architecture/app_model.md) (`target-after-slice`).

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
| [`model-assets/`](model-assets/) | standards / specifications / implementations / transformations |
| [`generated/`](generated/) | воспроизводимые артефакты (DAMS golden samples) |
| [`apps/viewer/`](apps/viewer/) | статический Publication Viewer (`publish.yaml` → `apps/viewer/dist`) |
| [`apps/cli/`](apps/cli/) | inbound CLI `moex-model` (`validate` / `lint` / `compile` / `diagram` / `diff` / `publish`) |
| [`apps/api/`](apps/api/) | FastAPI operational slice (conformance + validation runs) |
| [`packages/git-adapter/`](packages/git-adapter/) | `GitProvider` + local git backend |
| [`generated/contracts/`](generated/contracts/) | generated DAMS Pydantic (`moex_dams_contracts`) |
| [`packages/modeling-kernel/`](packages/modeling-kernel/) | envelopes + `StandardProvider` (TSpecBody ≠ TImplBody) |
| [`packages/standard-linkml/`](packages/standard-linkml/) | LinkML provider + ER-dictionary ingest |
| [`packages/specification-dams/`](packages/specification-dams/) | DAMS semantic rules, graph view, conformance |
| [`packages/publication/`](packages/publication/) | slice → PublicationModule / viewer JSON |
| [`packages/ontology/`](packages/ontology/) | FIBO CSV shim над [`packages/standard-owl/`](packages/standard-owl/) |
| [`tools/architecture-check/`](tools/architecture-check/) | механические проверки architecture pack |
| [`docs/architecture/`](docs/architecture/) | нормативная архитектура и связанные черновики |
| [`docs/migration/`](docs/migration/) | таблица переноса `model_src` → `model-assets` |
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | план Workbench MVP (подчинён MODELING_ARCHITECTURE) |

Миграция путей: [`docs/migration/model-src-to-model-assets.md`](docs/migration/model-src-to-model-assets.md).

## Быстрый старт

Нужен Python **3.11+** (на Windows часто удобнее `py -3.14`, если `python` указывает на 3.10).

### Publication Viewer

```bash
# из корня репозитория
py -3.14 -m pip install -e "./apps/viewer[dev]"
py -3.14 -m moex_publication_viewer.cli build --root .
# открыть apps/viewer/dist/index.html
```

Или `make viewer` / `make viewer-check` (если установлен `make`; можно задать `PYTHON=py -3.14`).

Новый раздел публикации: добавить `publish.yaml` рядом с источниками — без правок UI. Подробности: [`apps/viewer/README.md`](apps/viewer/README.md).

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
pip install -r requirements-linkml.txt
# from repo root:
linkml-lint --config .linkmllint.yaml model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml
```

Или `make validate-schemas`. Состав схем: [`model-assets/specifications/moex-dams/0.1/README.md`](model-assets/specifications/moex-dams/0.1/README.md).

### Первый вертикальный срез и CLI (Stage 0)

Основной запуск (кроссплатформенный, в т.ч. Windows без `make`):

```bash
python scripts/check_all.py
# или: powershell -NoProfile -File scripts/check_all.ps1
# или: make check
```

Порядок: `generate-contracts` → slice/CLI pytest (`apps/cli/scripts/check.ps1`) → `validate-schemas` → `validate-examples` → `validate-requirements` → `compare-golden` (contracts, JSON Schema, OWL, SHACL, DBML, Mermaid) → `architecture-check` → `publish-gate`.  
Флаги: `--keep-going`, `--only <step>`. Интерпретатор: `$PYTHON` / [`.python-version`](.python-version) / `apps/cli/.venv`.  
Pin: [`requirements-linkml.txt`](requirements-linkml.txt), CI: [`.github/workflows/check.yml`](.github/workflows/check.yml).

Регенерируемые артефакты схемы (кроме curated colored DBML):

```bash
make generate-artifacts
# or: moex-model compile --root . --artifacts
```

Пишет OWL/SHACL/`moex-dams.dbml`/Mermaid под [`generated/artifacts/moex-dams/0.1/`](generated/artifacts/moex-dams/0.1/) + manifests. `moex-dams-drawdb-colored.dbml` — ручной drawDB sample, не в golden.

Пишет [`model-assets/implementations/solutions/mdm/publications/vertical_slice.json`](model-assets/implementations/solutions/mdm/publications/vertical_slice.json) через `moex-model publish`.

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
| [docs/adr/](docs/adr/README.md) | Proposed — ADR-001–012 (Workbench / toolchain) |
| [MOEX Data Model Specification v0.1](docs/MOEX%20Data%20Model%20Specification%20v0.1%20на%20основе%20LinkML.md) | спецификация DAMS на LinkML |

## Именование

Метамодель и префикс — **DAMS** (`https://data.moex.com/dams/`, корневой файл `moex-dams.yaml`). Старый акроним MDMS не используется.

## Принципы (кратко)

1. Роли ≠ технологии: один формат может быть standard, specification или implementation.
2. Typed body стандарта живёт в provider schema, не в modeling kernel.
3. Specification body (schema) и implementation body (instance) — разные типы в API.
4. Git — реестр опубликованных активов; PostgreSQL/object storage — operational / derived.
5. Добавление нового стандарта не должно править classes kernel (`make architecture-check`).
