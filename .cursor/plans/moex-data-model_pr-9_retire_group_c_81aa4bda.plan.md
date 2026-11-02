---
name: "moex-data-model: PR-9 retire Group C"
overview: "Вывести 31 запись группы C из активного каталога требований без удаления: перенести три проверки, у которых нет другого дома, пометить записи deprecated и скрыть неактивные записи в viewer. Удаление строк, чистка requirement_refs и алиасов уходят в PR-10. Изменений LinkML-схемы нет, версия агрегата остаётся 5.4.0."
todos:
  - id: p9a-viewer-hide-inactive
    content: "PR-9a (apps/viewer): настройка requirements.show_inactive (по умолчанию выкл.), фильтр в filterExplorerItemsForPrefs, счётчики, тесты"
    status: completed
  - id: c1-rehome-conditionals
    content: "PR-9b, коммит 1: перенести PDM-001.c5 / PDM-002.c2 / PDM-002.c3 в Python (INV-065..067): матрица, фикстуры L2, алиасы, удалить шаблоны раннера, тесты"
    status: completed
  - id: c2-deprecate-group-c
    content: "PR-9b, коммит 2: пометить 31 запись группы C как deprecated с description про новый дом исполнения; сравнить assess до/после на эталонных моделях"
    status: completed
  - id: c3-docs-changelog
    content: "PR-9b, коммит 3: обновить ADR-056, requirements-inventory, IT_SOLUTION_MODEL_REQUIREMENTS §10, добавить CHANGELOG-requirements-retire-c.md и запись в changelog/constraint-matrix.md"
    status: completed
  - id: verify-gates
    content: "Проверить каждую ветку и каждый коммит отдельно: validate-schemas, validate-requirements, check-constraints, dams-packages-check, vertical-slice-check, viewer-check, make check; убедиться, что гейт публикации запускает L1"
    status: completed
isProject: false
---

# PR-9: вывод группы C из каталога (ADR-056)

Решение пользователя: записи группы C получают статус `deprecated`, не удаляются; неактивные записи скрываются в viewer. Удаление строк и чистка ссылок переезжают в PR-10.

Состояние git я не проверял. Этап делится на две ветки по правилу «одна тема на PR» (`multi-pr-series.mdc`): сначала viewer, потом данные.

- **PR-9a**, ветка `feat/viewer-hide-inactive-requirements`, от верхушки ветки PR-8. Тема: только `apps/viewer`.
- **PR-9b**, ветка `feat/requirements-backbone-pr9-retire-group-c`, поверх PR-9a. Тема: перенос трёх проверок и пометка записей. Схема и viewer не меняются.

PR-9a идёт первым, чтобы после пометки 31 записи в viewer не появилась стена серых строк. Группа A (14 записей `superseded`) уже сейчас видна и тоже скроется.

## Что помечается deprecated

**IT-solution (25 записей)** в [it-solution-requirements.yaml](model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml):
- PDM-001, PDM-002;
- PDM-005…PDM-020 (16 записей);
- ATR-001, ATR-006;
- REF-001;
- FLW-002…FLW-005.

**Концептуальный каталог (6 записей)** в [conceptual-model-requirements.yaml](model-assets/specifications/moex-dams/0.1/conceptual-model-requirements.yaml): CM-GEN-001, CM-GEN-002, CM-REF-001, CM-CON-003, CM-PDM-000, CM-PROP-001.

Размер каталога остаётся 74 записи (63 + 11), потому что ничего не удаляется. `test_export_requirements.py` не меняется. Группы A, B и D в PR-9 не трогаем.

Почему `deprecated`: норма перестала быть требованием каталога, заменяющего требования нет, исполнение живёт в схеме, Python и INV. `rejected` по смыслу неверен, `superseded` не может ссылаться на INV (`superseded_by` указывает на `SpecificationRequirement`).

## Что показала проверка кода

- **Где уже есть исполнение.**
  - Обязательность слотов закрыта `required` и `slot_usage` схемы в PR-8: `PDM-001.c1–c4/c6/c7`, `PDM-002.c1`, `ATR-001.c1/c3/c4`, `REF-001.c1/c2`.
  - PDM-005…020 и FLW-002…005 исполняются Python-функциями и имеют `INV` (INV-012…022, 033…041, 047, 059…064).
  - Типы атрибута: `DAMS-SEM-ATTR-TYPE` в `semantic_layer.py`. Концы связи: `references.py` (`DAMS-REF-005/006`). Уровни: `dams_levels.py` (`DAMS-LEVEL-002/003`). Genesis: `INV-043`. Область `ConceptualProperty`: `DAMS-SEM-PROP-SCOPE`.
- **Три проверки без другого дома.** Условные шаблоны раннера `pdm001_structure_ref`, `pdm002_scalar_type`, `pdm002_scalar_required` в [formal_checks.py](packages/specification-dams/src/moex_dams/rules/formal_checks.py). Раннер пропускает `deprecated` (`_INACTIVE_REQUIREMENT_STATUSES`, строка ~1353), поэтому без переноса они исчезнут.
- **Что остаётся нетронутым благодаря `deprecated`.** Матрица `constraint-matrix.yaml` с 25 `requirement_refs` (ссылки продолжают указывать на существующие строки), `DIAGNOSTIC_CODE_ALIASES`, аргументы `requirement_code=` в `technical_assets.py`, `data_structure.py`, `catalog_topology.py`, код `DAMS-REQ-PDM-009.c3`.
- **Viewer.** Статусы уже отображаются (`requirementStatusInfo`: «Отклонено», «Устарело», «Заменено»), но строки всех статусов показываются. Тест `test_requirement_status_ui.py` требует, чтобы `_load_requirement_items` по-прежнему возвращал `superseded`-строки, поэтому скрытие делается не в загрузчике, а на уровне представления.
- **Механизм настроек уже есть.** `apps/viewer/config/display.yaml` + `DEFAULT_DISPLAY_SETTINGS` в [config_loader.py](apps/viewer/src/moex_publication_viewer/config_loader.py) (ADR-015), читатель переопределяет через диалог настроек (localStorage). В `viewer.js` фильтры настроек собраны в `filterExplorerItemsForPrefs(items)` (скрытие корней, Glossary).

## PR-9a: viewer скрывает неактивные записи

- Новая настройка `requirements.show_inactive` (`bool`, по умолчанию `false`, группа `Navigation`, подпись про deprecated / superseded / rejected). Добавить в `display.yaml` и в `DEFAULT_DISPLAY_SETTINGS`.
- В `filterExplorerItemsForPrefs` ([viewer.js](apps/viewer/static/viewer.js)), когда настройка выключена:
  - рекурсивно убирать узлы с `attributes.kind === "requirement"` и статусом `deprecated`, `superseded` или `rejected` (тот же набор, что в `requirementStatusInfo` с `cls: "inactive"`);
  - убирать группы `section_folder`, в которых не осталось записей;
  - пересчитывать `attributes.requirement_count` на оставшиеся записи, чтобы бейджи в навигации совпадали (сейчас они берутся из Python и считают все строки).
- Скрытие только в боковой навигации, как у `navigation.hidden_roots`: поиск и прямые ссылки продолжают открывать скрытые записи, ссылка «заменено на» не ломается.
- Python-нормализатор `dams_explorer_roots.py` и экспорт требований не меняются. Альтернатива «фильтровать в Python и вообще не показывать» проще, но ломает поиск по старым кодам и `test_requirement_status_ui.py`.
- Тесты:
  - [test_display_prefs.py](apps/viewer/tests/test_display_prefs.py): добавить `requirements.show_inactive` в проверяемые ключи и подстроку функции фильтра в `viewer.js`;
  - [test_config.py](apps/viewer/tests/test_config.py): ключ присутствует, по умолчанию `False`;
  - новый тест на фильтр. Если JS нельзя запустить в pytest, проверять контракт по тексту `viewer.js`, как делают соседние тесты;
  - ручная проверка собранного viewer: с настройкой выключенной в «Требования» нет строк «Заменено»/«Устарело», с включённой они видны.
- Проверка: `make viewer-check`, `make check`. Файлы вне `apps/viewer` не меняются.

## PR-9b: коммиты

### Коммит 1: перенос трёх условных проверок (аддитивно)
- Новые Python-проверки: структура носителя в [technical_assets.py](packages/specification-dams/src/moex_dams/rules/technical_assets.py), тип и `required` скалярного узла в [data_structure.py](packages/specification-dams/src/moex_dams/rules/data_structure.py). Вызов подключить в `_run_l2_package_checks` и `check_formal_requirements`. Коды: `DAMS-INV-065` (`structure_ref` обязателен, кроме `in_memory`), `DAMS-INV-066` (у скаляра `native_type` или `data_type_ref`), `DAMS-INV-067` (скаляр объявляет `required`). Серьёзность `error`.
- В `constraint-matrix.yaml` добавить INV-065…067 по образцу INV-059…064: запись в `invariant_id_registry`, L2-фикстуры `valid`/`invalid` в `examples/invariants/l2/`.
- В `DIAGNOSTIC_CODE_ALIASES` внести `DAMS-REQ-PDM-001.c5`, `DAMS-REQ-PDM-002.c2`, `DAMS-REQ-PDM-002.c3`.
- Убрать три проверки из PDM-001/PDM-002 в каталоге и три шаблона из `_run_conditional`, чтобы не было дублей диагностик.
- Тесты в [test_formal_checks.py](packages/specification-dams/tests/test_formal_checks.py): `test_pdm002_scalar_type_required` теперь ждёт `DAMS-INV-066`, добавить тесты на INV-065 и INV-067.
- Проверка: `make check-constraints` (`--gate-strict`), `make dams-packages-check`.

### Коммит 2: пометка 31 записи `deprecated` (данные)
- В двух каталогах: `lifecycle_status: deprecated`. В `description` указать новый дом исполнения (схема, `INV-NNN` или Python-модуль). Строки не удаляются, `requirement_refs`, алиасы и `requirement_code=` не трогаются.
- После этого коммита раннер перестаёт выдавать `model-requirements` slot_required для PDM-001, PDM-002, ATR-001, REF-001. Эти слоты теперь ловит L1 (схема).
- Контроль: прогнать body assess на четырёх эталонных моделях и примерах до и после коммита и сравнить наборы кодов. Ожидаемое отличие только в проверках из схемы (`PDM-001.*`, `PDM-002.c1`, `ATR-001.c1/c3/c4`, `REF-001.c1/c2`). Диагностики PDM-005…020, FLW-002…005 не должны исчезнуть: они идут через Python и INV.
- Тесты `test_formal_checks.py` с ожиданием `PDM-001`/`system_ref` из каталога перенести на L1 или убрать с пометкой, что покрытие даёт схема и `validate-examples`.

### Коммит 3: документы
- [ADR-056](docs/adr/ADR-056-requirements-backbone.md): статус «PR-0…PR-9 landed», итог PR-9 в D4/D5. Явно записать, что PR-10 удаляет `deprecated` и `superseded` строки.
- [requirements-inventory.md](docs/migration/requirements-inventory.md): итоговый дом каждой записи группы C.
- [IT_SOLUTION_MODEL_REQUIREMENTS.md](docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md): раздел 10, строки группы C помечены deprecated.
- Новый `docs/migration/CHANGELOG-requirements-retire-c.md` и запись в `docs/changelog/constraint-matrix.md` (INV-065…067). `docs/architecture/constraint-matrix.md` перегенерировать: `scripts/check_constraint_matrix.py --write-doc`.

## Проверка каждой ветки и коммита отдельно
`make validate-schemas`, `make validate-requirements`, `make check-constraints`, `make dams-packages-check`, `make vertical-slice-check`, `make viewer-check`, `make check`. После `vertical-slice-check` убедиться, что `vertical_slice.json` не изменились.

## Что переезжает в PR-10
- Удаление `deprecated` и `superseded` строк (группы A и C, 14 + 31) и падение каталога до 43 записей; правка счётчика в `test_export_requirements.py`.
- Чистка 25 `requirement_refs` в матрице и описания в `constraint-matrix.schema.yaml`.
- Чистка `DIAGNOSTIC_CODE_ALIASES` и аргументов `requirement_code=`, замена `DAMS-REQ-PDM-009.c3` на `DAMS-INV-034`.
- Группа D, судьба LDM-006/REF-002, GEN-003, формулировки CDM-01/LDM-04, политика кодов backbone-записей.

## Риски и допущения
- **Потеря slot_required в assess.** После пометки обязательность слотов ловит только L1. Убедиться, что гейт публикации запускает L1 (`validate-examples`, `publish-gate`) на моделях решений.
- **Производный скелет модели.** `model_skeleton_projection` строит «Спецификацию модели» из `formal_checks` каталога и не смотрит на статус. Deprecated-строки останутся в скелете. В PR-9 это допустимо (скелет не меняется), но к PR-10 нужно решение: после удаления строк обязательные слоты возьмёт `minimal_schema_projection`.
- **Скрытые записи и код в диагностиках.** Диагностики продолжают ссылаться на коды deprecated-записей (`DAMS-REQ-PDM-0xx`). Строка скрыта в навигации, но открывается поиском и по ссылке, поэтому трассируемость сохраняется.
- **Три концептуальные записи** (CM-GEN-002, CM-PDM-000, CM-PROP-001) остаются на `dams_levels.py` и `semantic_layer.py` без новых INV. Если нужны INV, это отдельный маленький коммит в PR-9b до пометки.
