---
id: known-gaps
sources:
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-003-postgres-operational.md
  - docs/adr/ADR-045-executable-constraint-matrix.md
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/architecture/linkml_architecture.md
  - docs/guides/adding-an-invariant.md
  - README.md
  - apps/api/src/moex_model_api/db/session.py
  - infra/compose/postgres.yml
  - docs/adr/ADR-058-airgap-image-deploy.md
  - model-assets/external-sources/fibo/registry.yaml
  - model-assets/implementations/manifest.lock
draft: true
---

# Известные расхождения

Несколько файлов говорят об одном и том же по-разному. Ниже только то, что сверено с самими файлами. Эти файлы здесь не правятся: каждый пункт — отдельная правка, когда её решат делать.

Если тексты спорят, порядок такой. Сначала принятое решение в `docs/adr/`. Затем [MODELING_ARCHITECTURE.md](docs/architecture/MODELING_ARCHITECTURE.md) и схемы. Затем код и каталог `model-assets/`. Страницу в `docs/user/` в этом случае исправляют. Ниже у каждого пункта сказано, какая сторона в этом порядке права.

Черновик рабочей среды в конце пишет, что проекты решений имеют статус Proposed. Это [linkml_architecture.md](docs/architecture/linkml_architecture.md), сам файл в статусе Draft. У многих решений в собственной шапке статус Accepted. Права шапка решения: принятое решение стоит выше черновика. Фраза в конце черновика устарела.

У [MODELING_ARCHITECTURE.md](docs/architecture/MODELING_ARCHITECTURE.md) в шапке сразу `status: Proposed` и `normative: true`. Корень репозитория зовёт этот файл нормативным и тут же пишет, что он Proposed 0.2. Пока статус Proposed, файл не перекрывает принятое решение. Слово «нормативный» не делает его принятым. На три роли продукта по-прежнему опираются здесь, потому что отдельного принятого решения про них нет. Где файл расходится с принятым решением, побеждает решение.

Единственная инструкция, как добавить строку в матрицу проверок, — [adding-an-invariant.md](docs/guides/adding-an-invariant.md). У неё статус Proposed. Само решение [ADR-045](docs/adr/ADR-045-executable-constraint-matrix.md) принято. Корень репозитория указывает на инструкцию как на руководство и не говорит, что она не принята. Правы принятое решение и матрица проверок. Инструкция — записанный порядок, по ней нельзя рассказывать, будто так уже решено.

[ADR-058](docs/adr/ADR-058-airgap-image-deploy.md) выносит модели в отдельный репозиторий и не принят. Файл `model-assets/external-sources/fibo/registry.yaml` в поле `upstream_url` указывает на фикстуру `packages/external-sources/tests/fixtures/mini_ontology`. Этот каталог в репозиторий моделей не входит. Права граница в решении: фикстуру туда не кладут. Ссылку в реестре этим не переписывают.

На дереве с переводами строк LF команды `moex-model check-manifest --root .` и `moex-model lock verify --root .` расходятся по четырём реализациям: crm, esed, mdm, ucd. Хеш в `model-assets/implementations/manifest.lock` не совпадает с разобранным телом файла. Фиксацию здесь не переписывают.

[ADR-003](docs/adr/ADR-003-postgres-operational.md) предлагает сделать [операционным хранилищем](glossary:operational-store) PostgreSQL и не принят. В тексте самого решения сказано, что на текущем срезе этой базы нет. Рядом уже лежат два файла. Служебный интерфейс по умолчанию открывает SQLite в памяти: `apps/api/src/moex_model_api/db/session.py`. Файл `infra/compose/postgres.yml` поднимает PostgreSQL, и в общую проверку он не входит. Права принятая сторона: опубликованная модель живёт в Git ([ADR-002](docs/adr/ADR-002-git-published-source.md)). Непринятое решение не делает базу устройством продукта. SQLite и compose — локальный запуск и заготовка, не принятое хранилище.
