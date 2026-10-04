# Solution xlsx import (Object / ObjectAttribute → DAMS)

**ADR:** [ADR-022](../adr/ADR-022-solution-xlsx-import.md)

Импорт моделей ИТ-решений из книги с листами `Object` / `ObjectAttribute`
в канонические YAML под `model-assets/implementations/solutions/{slug}/`.

## Быстрый старт

```powershell
# Один раз: поднять зависимости publication/cli (contracts + dams + linkml)
powershell -NoProfile -ExecutionPolicy Bypass -File packages/publication/scripts/check.ps1

# Импорт (xlsx вне git)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/import-solution-xlsx.ps1 `
  -Xlsx "F:\...\solution_src\src_soluitions_model.xlsx" `
  -System MDM -Force

# Все четыре системы
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/import-solution-xlsx.ps1 `
  -Xlsx "F:\...\src_soluitions_model.xlsx" -All -Force

# ЕСЭД: в PowerShell удобнее -System ESED (алиас → кириллический SrcSystem)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/import-solution-xlsx.ps1 `
  -Xlsx "F:\...\src_soluitions_model.xlsx" -System ESED -Force
```

Эквивалент через CLI (нужен `PYTHONPATH` или editable install `apps/cli`):

```text
moex-model import-solution --xlsx <path> --system MDM|UCD|CRM|ЕСЭД --force
```

Профиль по умолчанию:
[`model-assets/implementations/solutions/solution-xlsx.profile.yaml`](../../model-assets/implementations/solutions/solution-xlsx.profile.yaml).

Отчёты: `tmp/solution-import/<slug>/import-report.md` (+ `.json`).

После импорта:

1. Зарегистрируйте Impl в
   [`architecture-catalog.yaml`](../../model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml)
   (`role: specification_implementation`, `conforms_to: moex-dams`, `module_id`).
   Без записи в каталоге модуль есть в HTML, но **не** появляется в
   `moex.dams → Реализации`.
2. Пересоберите viewer:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1
```

В дереве `moex.dams → Реализации` появятся MDM / UCD / CRM / ЕСЭД
(`moex:module:{mdm,ucd,crm,esed}-solution`).

## Что куда пишется

| Файл | Роль |
|------|------|
| `{slug}-solution-model.yaml` | Канон ModelPackage (редактировать здесь) |
| `implementation.yaml` | Envelope ADR-021 (`dams-data-model` / `solution`) |
| `publish.yaml` | Publication module (создаётся, если нет) |
| `publications/vertical_slice.json` | Assess + graph projection |

Исходный xlsx **не** коммитится. В envelope — `filename#sha256:…`, не `file:///…`.

## Режим данных

- **A (v1):** в модель только target-строки (`ObjectCode` + `AttributeCode`).
- Physical/mappings — если заполнен `SrcAttributeCode`.
- **src-only** строки → только отчёт (`SXI-SRC-010`). Roadmap B: `src_only: physical` в профиле.

## Проверки

Два контура:

1. **SXI-*** — входной реестр (лист/строка/колонка + RU remediation).
2. **ASSESS:*** — `moex_dams.assess_implementation` (GEN/LDM/ATR/REF/PDM).

Коды SXI (кратко): `SXI-SRC-*`, `SXI-OBJ-*`, `SXI-ATTR-*`, `SXI-KEY-*`, `SXI-FK-*`, `SXI-PHY-001`, `SXI-IO-001`, `SXI-VAL-001`, `SXI-MAP-001`.

Exit codes: `0` ok, `1` error, `2` usage, `3` файл не перезаписан (черновик в report-dir).

`--strict` повышает warning → error. Без `--force` существующий YAML не затирается.

## Редактирование после bootstrap

1. Править `{slug}-solution-model.yaml` (сущности, title, governance, realizes на enterprise).
2. Известные follow-up:
   - UCD: опечатка `EMPOYEE` в источнике — переименовать вручную при необходимости.
   - `conceptual_alignment_status: pending` + локальные realizes на stub-концепты — выверить с enterprise conceptual.
   - Технология / `system_ref` — в профиле `systems[]`.
3. Повторный импорт: без `--force` сравнить draft в `tmp/solution-import/` (`moex-model semantic-diff`).

## Тесты

```powershell
packages/standard-linkml/.venv/Scripts/python -m pytest `
  packages/standard-linkml/tests/test_solution_xlsx_normalize.py `
  packages/standard-linkml/tests/test_solution_xlsx_source.py `
  packages/standard-linkml/tests/test_solution_xlsx_rules.py `
  packages/standard-linkml/tests/test_solution_xlsx_convert.py `
  tests/architecture/test_import_boundaries.py -q
```

Fixture workbook: `packages/standard-linkml/tests/fixtures/solution-xlsx/`
(`build_fixture_xlsx.py` пересобирает `fixture.xlsx`).
