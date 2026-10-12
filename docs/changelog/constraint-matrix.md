---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Changelog: executable constraint matrix (ADR-045)

Журнал серии PR-C0..C5. Тексты инвариантов не дублируются: см. матрицу (с PR-C1) и [constraint-matrix-inventory-report.md](../architecture/constraint-matrix-inventory-report.md).

## PR-C0: инвентаризация и spike (схемы и `generated/**` не менялись)

**Добавлено**

- `scripts/inventory_invariants.py`, `docs/architecture/invariant-candidates.csv` (150 кандидатов).
- [ADR-045](../adr/ADR-045-executable-constraint-matrix.md) (Proposed) и строка в индексе ADR.
- [linkml-rules-support.md](../architecture/linkml-rules-support.md): таблица «правило x генератор», версия LinkML 1.11.1.
- [constraint-matrix-inventory-report.md](../architecture/constraint-matrix-inventory-report.md): 17 существующих правил, прочие кандидаты, расхождения, вопросы.
- Spike: `tmp/constraint-spike/` (позднее архив — тег `archive/constraint-spike`, PR-C6).

**Стало строже:** ничего.

**Затронутые данные:** нет.

**Найдено (не исправлялось, см. вопросы Q1-Q8 отчёта):** `Validator(schema)` без плагинов в `validate-*` не проверяет данные; INV-001 неисполним в JSON Schema; `ABSENT` на нескольких слотах ослаблен (INV-013, INV-015, INV-017); CRLF в `requirements-linkml.txt` ломает golden на Windows.

## PR-C1a: validation helper (основа для negative-режима)

**Добавлено**

- `moex_standard_linkml.validation.make_linkml_validator` + `error_results`.
- Проводка в `adapters/validator.py`, `ingest/validate.py`, `validate-examples.ps1`, `validate-schemas.ps1`.
- Тесты `packages/standard-linkml/tests/test_validation_helper.py`.
- Отчёт [validation-helper-c1a-report.md](../architecture/validation-helper-c1a-report.md): список данных, которые станут невалидными; таблица `source_status` для INV-001..017.

**Стало строже:** примеры и ModelPackage реально проверяются JSON Schema (closed); xlsx-ingest больше не пишет `name` на `Mapping`.

**Затронутые данные:** `requirements/examples/it-solution-model.example.yaml` (убран `name` у mappings).

**Отложено:** `validate-requirements` остаётся на vacuous `Validator` — каталог `it-solution-requirements.yaml` даёт 18 ошибок под плагином (`description`/`effective` на FormalCheck). См. отчёт C1a.

## PR-C1: constraint matrix

**Добавлено**

- `model-assets/.../constraints/constraint-matrix.schema.yaml` + `constraint-matrix.yaml` (INV-001..027).
- `scripts/check_constraint_matrix.py`, цель `check-constraints` в Makefile и `scripts/check_all.py`.
- Автогенерируемый [constraint-matrix.md](../architecture/constraint-matrix.md).
- Руководство [adding-an-invariant.md](../guides/adding-an-invariant.md).
- Тесты `packages/specification-dams/tests/test_constraint_matrix.py`.
- Пин `ruamel.yaml==0.18.10` в `requirements-linkml.txt` + обновление `toolchain_digest` бандла.

**Стало строже:** любой новый `rules` в схемах без строки матрицы ломает `check-constraints`; baseline 17 правил закреплён SHA + sha256.

**Статусы:** INV-001..017 = `implemented-untested`; INV-018..027 = `planned` (нумерация закреплена).

**Затронутые данные:** нет правок условий LinkML `rules`.

## PR-C2: L1 INV-prefix + negative fixtures

**Добавлено**

- Префикс `INV-NNN:` в `description` 17 существующих `rules` (условия не менялись).
- `examples/invariants/` — 17× valid/invalid + `manifest.yaml`; negative-режим в `validate-examples.ps1`.
- Пути `tests.l1_*` в матрице; тест `test_invariant_l1_fixtures.py`.

**Стало строже:** `validate-examples` требует, чтобы invalid-фикстуры отвергались JSON Schema.

**Версия схемы:** `3.0.0` **не** бампим в C2 (только описания rules; поведение валидации не меняется). Решение о PATCH `3.0.1` — на момент публикации релиза: если `3.0.0` ещё не опубликован, digest становится окончательным для `3.0.0`; если уже опубликован — нужен `3.0.1` (одна версия не должна иметь два digest).

**Публикуемые артефакты:** изменились `content_digest` у `doc`, `ontology-profile` и бандла (корневой `schema_digest` без изменений). Потребители, закрепляющие digest бандла, увидят новое значение при той же схеме `3.0.0`.

**Golden:** обновляется отдельным коммитом после проверки diff (Q6).

**Не чинить в C2/C3 (семантика → отдельная серия / MAJOR 4.0.0):** INV-001 L1 boolean defect (`l1_positive: not_satisfiable`, уровни L2+L3); multi-ABSENT INV-013/015/017 оставляем ослабленными на L1, закрываем L2/L3.

## PR-C3: L2 validators

**Добавлено**

- L2 `DAMS-INV-001` (`check_identifying_requires_is_identifying`), `DAMS-INV-010/011/014` в `data_structure.py`.
- `invariant_id` на существующих PDM-проверках: INV-012…022, INV-015/016/017 (message_refs), INV-018; INV-026 на `MOEX-ONT-004`.
- Unit-тесты `packages/specification-dams/tests/test_invariant_l2.py` (valid/invalid).
- Заметка Q-INV-011 / AsyncAPI в [ADR-045](../adr/ADR-045-executable-constraint-matrix.md); отчёт [constraint-matrix-c3-report.md](../architecture/constraint-matrix-c3-report.md).

**Не изобреталось:** INV-023/024/027 (`source_status: partial`); INV-025 (нет instance-валидатора tags в `moex_dams/rules`).

**INV-011:** правило не менялось; расхождение с AsyncAPI остаётся вопросом в ADR-045.

**Стало строже:** L2 теперь ловит INV-001/010/011/014 на пакетах (ранее только L1 JSON Schema / без L2). Данные автоматически не чинились.

**Статусы:** INV-018…022, INV-026 → `implemented-untested`; INV-010/011/014 получили уровень L2 в матрице; INV-023…025, 027 остаются `planned`.

## PR-C3a: checker logic in package

**Добавлено**

- Логика проверки матрицы перенесена в `moex_dams.rules.constraint_matrix`.
- `scripts/check_constraint_matrix.py` — тонкая CLI-обёртка (поведение без изменений).

**Стало строже:** ничего (рефакторинг).

## PR-C3b: checker v2 (level_status + runners)

**Добавлено**

- `level_status` (L1/L2/L3) в схеме и матрице; общий `status` должен совпадать с вычислением.
- `adr_ref` обязателен при `waived`.
- Проверка префикса `INV-NNN:` в `description` каждого `rules`.
- L1/L2 runners: при `level_status.*.implemented` valid проходит, invalid падает (L2 — только YAML-фикстуры).

**Статусы:** L1 у INV-002…017 → `implemented`; L2 у tagged кандидатов → `implemented-untested` до C3c; L3 → `planned`.

## PR-C3c: L2 YAML fixtures

**Добавлено**

- `examples/invariants/l2/INV-*.{valid,invalid}.yaml` для INV-001/010–022/026.
- Матрица: `l2_valid`/`l2_invalid` → YAML; `level_status.L2=implemented` где L2 заявлен.
- Тест `test_l2_yaml_fixtures_cover_tagged_invariants`.

**Статусы:** INV-018/019/021/022/026 → `implemented`; INV с L3 остаются `implemented-untested`.

## PR-C3d: validate-requirements plugin

**Добавлено**

- Слоты `FormalCheck.description` и `FormalCheck.effective` в `moex-requirements.yaml`.
- `validate-requirements.ps1` → `make_linkml_validator` (closed JSON Schema).
- Обновлён отчёт C1a (deferred → done).

**Затронутые данные:** каталог не менялся; схема расширена (additive). Golden — отдельный коммит при смене digest.

## PR-C4a: L1 waivers + INV-011 AsyncAPI

**Добавлено**

- L1 `waived` (+ `adr_ref: ADR-045`) для INV-001, INV-013, INV-015, INV-017.
- INV-011: L1+L2 допускают `schema_format=other` для AsyncAPI dialect; `source_status=aligned`.
- Amendment в ADR-045.

**Стало строже / слабее:** INV-011 послабление (additive any_of).

## PR-C4b: L3 SHACL

**Добавлено**

- Ручные формы `constraints/shacl/manual/invariants.ttl` (`sh:sourceShape` → INV-001…017).
- RDF fixtures `examples/invariants/l3/*.ttl`; тесты `test_invariant_l3.py`.
- Явные `SHACL_OPTIONS` в `generate_artifacts.py`; тест что gen-shacl не эмитит INV.
- Дифференциальные spot-check L1↔L3 (INV-002) и L2↔L3 (INV-010).
- INV-020 L3 → `waived` (циклы остаются на L2).

## PR-C5: gate and Accepted

**Добавлено**

- `invariant_id_registry` (append-only); baseline снят.
- INV-023/024/025/027 → `waived` + `adr_ref: ADR-045`.
- `--gate-strict` / publish-gate вызывает `run_check(..., gate_strict=True)`.
- ADR-045 → Accepted; ссылки в README, MODELING_ARCHITECTURE §14, `constraint-matrix-p0-audit.md`.

## PR-C6: cleanup

**Удалено**

- `tmp/constraint-spike/` (архив: тег `archive/constraint-spike`).
- `.tmp-pdf-extract/` (5 txt); запись в `.gitignore`.

**Документы:** ссылки на spike заменены на тег.

## ADR-046 PR-4: typed Mapping endpoint invariants

**Добавлено**

- INV-028..032 (L1; INV-028 also L3): designator rules на `RealizesMapping` /
  `EntityPhysicalMapping` / `FieldMapping` / `AlignsWithMapping` (`INV-NNN:` в
  `moex-core.yaml`, fixtures; manual SHACL SPARQL for designators).
- INV-033..036 (L2+L3): direction-aware endpoint kinds; `check_mapping_endpoint_types`
  + manual SHACL (EntityPhysical maxCount 1, AlignsWith http(s)).
- INV-037 (L3): FieldMapping `SchemaNodeRef` pattern (gen-shacl miss).
- PDM-009 statement обновлён на направление source→target (ADR-046).

**Стало строже:** entity_physical / field_mapping проверяют направление концов, не только
наличие пары классов; realizes / aligns_with покрыты явными INV.
