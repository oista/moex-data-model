---
id: applications
sources:
  - docs/adr/ADR-004-modular-monolith.md
  - docs/adr/ADR-005-drawdb-isolated.md
  - docs/adr/ADR-007-pydantic-dto-not-validator.md
  - Makefile
  - apps/cli/README.md
  - apps/viewer/README.md
  - apps/api/README.md
  - apps/web/README.md
  - apps/drawdb/README.md
draft: true
---

# Приложения

Приложения — это программы, которыми пользуются. Они лежат в `apps/`. Правила модели в этих каталогах не живут: программа вызывает пакеты кода, а пакеты читают YAML. Так продукт остаётся одним контуром запуска с жёсткими границами папок (ADR-004).

`apps/cli` — программа `moex-model`: проверить модель, собрать производные файлы, открыть публикацию. Своих правил DAMS здесь нет, их выполняет `packages/specification-dams`. Проверка самой программы входит в общую проверку шагом `slice-cli`.

`apps/viewer` — статический просмотр. `make viewer` собирает HTML публикации модели, `make viewer-serve` открывает его локально на порту 8765. `make user-docs` собирает этот текст. В общую проверку входит только `user-docs`. Сборка HTML публикации модели — отдельная цель.

`apps/api` — служебный HTTP-интерфейс поверх тех же пакетов. Ему нужны классы из `generated/contracts/moex-dams/0.1`. Эти классы описывают форму запроса и ответа. Проверку модели они не выполняют: её делают LinkML и правила в `packages/specification-dams` (ADR-007). Локально интерфейс поднимается на SQLite. Цель `make api-check` в общую проверку не входит.

`apps/web` — веб-приложение поверх `apps/api`: редактор YAML и страница схемы. Цели `make web-check` и `make web-e2e` в общую проверку не входят.

`apps/drawdb` — отдельное приложение схем. Его исходники в веб-приложение не вшивают. С моделью оно говорит через DBML и пакет `packages/drawdb-adapter` (ADR-005). Поднять его локально можно целью `make drawdb-up`. В общую проверку эта цель не входит. Проверка моста — `make drawdb-adapter-check`, тоже вне общей проверки.

Где прочитать решения: [ADR-004](docs/adr/ADR-004-modular-monolith.md), [ADR-005](docs/adr/ADR-005-drawdb-isolated.md), [ADR-007](docs/adr/ADR-007-pydantic-dto-not-validator.md).
