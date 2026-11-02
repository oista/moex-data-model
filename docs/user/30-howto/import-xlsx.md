---
id: import-xlsx
sources:
  - docs/adr/ADR-022-solution-xlsx-import.md
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
  - docs/dev/solution-xlsx-import.md
  - model-assets/implementations/solutions/solution-xlsx.profile.yaml
  - model-assets/implementations/manifest.yaml
  - model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml
  - scripts/import-solution-xlsx.ps1
  - apps/cli/src/moex_model_cli/__main__.py
draft: true
---

# Импорт из таблицы

Модели решений приходят книгой Excel с листами `Object` и `ObjectAttribute`. Команда `moex-model import-solution` переносит одну систему в YAML [реализации](glossary:specification-implementation) (ADR-022). Книгу в Git не кладут. Дальше правят уже YAML: это [опубликованный источник](glossary:published-source).

Из корня репозитория:

```text
moex-model import-solution --xlsx путь\к\книге.xlsx --system MDM --root .
```

Система — одно из MDM, UCD, CRM, ЕСЭД. Профиль колонок по умолчанию лежит в `model-assets/implementations/solutions/solution-xlsx.profile.yaml`. YAML пишется в `model-assets/implementations/solutions/<краткое имя из профиля>/`, например `solutions/mdm/`. Для ЕСЭД краткое имя — `esed`. Если такой файл уже есть, команда его не затирает. Чтобы заменить, нужен `--force`. Без него черновик остаётся в отчёте `tmp/solution-import/`, а команда заканчивается с кодом 3. Та же последовательность есть обёрткой `scripts/import-solution-xlsx.ps1`. Коды отчёта разобраны в [solution-xlsx-import.md](docs/dev/solution-xlsx-import.md).

Команда сама создаёт `publish.yaml` рядом с пакетом, если файла ещё нет. Новый каталог общая проверка не видит, пока его нет в [описи состава](glossary:repository-manifest): строка в `model-assets/implementations/manifest.yaml` и затем `moex-model lock update --root .` (ADR-047). Чтобы модуль встал в ветку «Реализации», нужна ещё запись в `architecture-catalog.yaml`.

Где прочитать решение: [ADR-022](docs/adr/ADR-022-solution-xlsx-import.md).
