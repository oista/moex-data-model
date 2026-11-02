---
id: normative-docs
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/architecture/CHECKLIST.md
  - docs/architecture/constraint-matrix.md
  - docs/architecture/constraint-matrix-p0-audit.md
  - docs/architecture/identity-map.md
  - docs/architecture/provider-protocol-test-spec.md
  - docs/architecture/viewer-decisions.md
  - docs/architecture/app_model.md
  - docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md
  - docs/architecture/linkml_architecture.md
  - docs/architecture/ontology-catalog.md
  - docs/architecture/MOEX_PARTY_AND_TRADING_PARTICIPATION_PROFILE.md
  - docs/architecture/linkml-rules-support.md
  - docs/architecture/constraint-matrix-c3-report.md
  - docs/architecture/constraint-matrix-inventory-report.md
  - docs/architecture/model-element-matrix-before.md
  - docs/architecture/validation-helper-c1a-report.md
  - docs/architecture/model-element-inventory-report.md
  - docs/architecture/modeling-kernel.yaml
  - docs/architecture/uml/description.md
draft: true
---

# Нормативные документы

В `docs/architecture/` лежат длинные заметки об устройстве продукта. Эта документация их не заменяет и новых правил не вводит. Статус смотрят в шапке файла. Принят — на него можно опираться. Proposed и Draft — записано, но ещё не принято. Historical — старый снимок, не текущее описание.

Файл, на который указывает корень репозитория, — [MODELING_ARCHITECTURE.md](docs/architecture/MODELING_ARCHITECTURE.md). Он всё ещё Proposed, хотя в шапке помечен как нормативный. Пока так, при споре с принятым решением побеждает решение.

| Файл | Статус | Зачем он |
|---|---|---|
| [MODELING_ARCHITECTURE.md](docs/architecture/MODELING_ARCHITECTURE.md) | Proposed | Длинное описание устройства. На него ссылается корень репозитория. |
| [CHECKLIST.md](docs/architecture/CHECKLIST.md) | Accepted | Вопросы для разбора архитектуры. |
| [constraint-matrix.md](docs/architecture/constraint-matrix.md) | Accepted | Таблица проверок. Её пишет скрипт сверки матрицы, руками не правят. |
| [constraint-matrix-p0-audit.md](docs/architecture/constraint-matrix-p0-audit.md) | Accepted | Закрытие первого разбора этой таблицы. |
| [identity-map.md](docs/architecture/identity-map.md) | Accepted | Какой номер отвечает на вопрос «что изменилось». |
| [provider-protocol-test-spec.md](docs/architecture/provider-protocol-test-spec.md) | Accepted | Как проверять общий протокол стандарта. Сама проверка отложена. |
| [viewer-decisions.md](docs/architecture/viewer-decisions.md) | Accepted | Старые решения о просмотре. Шапка указывает, что их заменяет MODELING_ARCHITECTURE.md. |
| [app_model.md](docs/architecture/app_model.md) | Draft | Черновик раскладки пакетов. |
| [IT_SOLUTION_MODEL_REQUIREMENTS.md](docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md) | Draft | Черновик требований к модели ИТ-решения. |
| [linkml_architecture.md](docs/architecture/linkml_architecture.md) | Draft | Черновик рабочей среды. Это не верхний уровень архитектуры. |
| [ontology-catalog.md](docs/architecture/ontology-catalog.md) | Draft | Черновик каталога внешних спецификаций. |
| [MOEX_PARTY_AND_TRADING_PARTICIPATION_PROFILE.md](docs/architecture/MOEX_PARTY_AND_TRADING_PARTICIPATION_PROFILE.md) | Proposed | Срез понятий предприятия. Не принят. |
| [linkml-rules-support.md](docs/architecture/linkml-rules-support.md) | Proposed | Какие правила схемы умеют генераторы. |
| [constraint-matrix-c3-report.md](docs/architecture/constraint-matrix-c3-report.md) | Proposed | Отчёт о проверках второго уровня. |
| [constraint-matrix-inventory-report.md](docs/architecture/constraint-matrix-inventory-report.md) | Proposed | Отчёт инвентаризации матрицы проверок. |
| [model-element-matrix-before.md](docs/architecture/model-element-matrix-before.md) | Proposed | Снимок до разложения общего класса схемы. |
| [validation-helper-c1a-report.md](docs/architecture/validation-helper-c1a-report.md) | Proposed | Отчёт о помощнике проверки. |
| [model-element-inventory-report.md](docs/architecture/model-element-inventory-report.md) | Historical | Старый снимок инвентаризации. |
| [modeling-kernel.yaml](docs/architecture/modeling-kernel.yaml) | шапки со статусом нет | Схема ядра ролей: стандарт, спецификация, реализация. |
| [uml/description.md](docs/architecture/uml/description.md) | шапки со статусом нет | Пояснение к рисункам. Рисунки иллюстрируют схему, нормой не являются. |

Файлы `.csv` рядом с отчётами — таблицы к этим отчётам. Их не читают как описание продукта. Рисунки лежат в `docs/architecture/uml/`.
