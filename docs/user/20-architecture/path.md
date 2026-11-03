---
id: architecture-path
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-011-reproducible-artifacts.md
  - Makefile
  - scripts/check_all.py
draft: true
---

# Общая схема

Продукт устроен как один путь из четырёх шагов. Каждый шаг лежит в своём каталоге, и следующий шаг читает только результат предыдущего.

1. Модель правят в YAML в каталоге `model-assets/`. Для DAMS это файлы на языке [LinkML](glossary:linkml). Коммит в Git и есть [опубликованный источник](glossary:published-source).
2. Общая проверка читает эти файлы и говорит, сходятся ли они с правилами. Точка входа — `scripts/check_all.py`, та же последовательность, что у `make check`. В неё входят схемы, примеры, [матрица проверок](glossary:constraint-matrix), опись пакетов, топология, назначения, ворота публикации и сборка этого текста.
3. Каталог `generated/` собирается из YAML заново. `generated/contracts/` — классы для служебного интерфейса. `generated/artifacts/` — OWL, SHACL, DBML и соседние виды. Это [производные файлы](glossary:derived-artifact): их можно удалить и получить снова той же сборкой (ADR-011). Руками их не правят. Шаг `compare-golden` как раз сверяет уже лежащие файлы с повторной сборкой.
4. Просмотр модели — HTML, который собирает `apps/viewer` командой `make viewer`. Текст, который вы читаете, — отдельный файл `docs/user/index.html`. Его собирает `make user-docs`, и этот шаг входит в общую проверку. Сборку просмотра модели общая проверка не запускает.

Правило записано в [ADR-011](docs/adr/ADR-011-reproducible-artifacts.md).
