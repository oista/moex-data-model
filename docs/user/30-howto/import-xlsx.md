---
id: import-xlsx
sources:
  - docs/adr/ADR-022-solution-xlsx-import.md
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
  - docs/dev/solution-xlsx-import.md
  - model-assets/implementations/solutions/solution-xlsx.profile.yaml
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

Система — одно из MDM, UCD, CRM, ЕСЭД. Профиль колонок по умолчанию лежит в `model-assets/implementations/solutions/solution-xlsx.profile.yaml`. YAML пишется в `model-assets/implementations/solutions/<имя>/`. Если такой файл уже есть, команда его не затирает. Чтобы заменить, нужен `--force`. Без него черновик остаётся в отчёте `tmp/solution-import/`, а команда заканчивается с кодом 3. Та же последовательность есть обёрткой `scripts/import-solution-xlsx.ps1`. Коды отчёта разобраны в [solution-xlsx-import.md](docs/dev/solution-xlsx-import.md).

Новый каталог решения общая проверка ещё не видит, пока его нет в [описи состава](glossary:repository-manifest). Дальше тот же порядок, что у любой реализации: строка в `model-assets/implementations/manifest.yaml`, команда `moex-model lock update --root .`, файл `publish.yaml` рядом с пакетом и запись в `architecture-catalog.yaml` (ADR-047).

Где прочитать решение: [ADR-022](docs/adr/ADR-022-solution-xlsx-import.md).
