---
id: model-package
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
  - docs/adr/ADR-054-repository-aggregates-and-manifest.md
draft: true
---

# Пакет и репозиторий моделей

Конкретную модель данных пишут как [модельный пакет](glossary:model-package). Пакет бывает двух уровней. Общая модель предприятия задаёт смысл. Модель решения на неё опирается. Отдельного «логического пакета» нет.

Общая модель предприятия лежит в `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml`. Модели решений — в `model-assets/implementations/solutions/`, например `solutions/mdm/mdm-solution-model.yaml`.

Несколько пакетов вместе образуют [репозиторий моделей](glossary:model-repository). Его не хранят одним гигантским файлом. На проверке он собирается из документов, перечисленных в [описи состава](glossary:repository-manifest): `model-assets/implementations/manifest.yaml`. Опись правят руками, когда документ добавляют, убирают или переносят.

Рядом [фиксация состава](glossary:repository-lock) — файл `model-assets/implementations/manifest.lock`. Его переписывает только `moex-model lock update --root .`. Проверка файл не переписывает: `moex-model lock verify --root .` или `make lock-verify`. В общую `make check` входят и проверка описи (`make check-manifest`), и проверка фиксации.

Где прочитать решение: [ADR-047](docs/adr/ADR-047-repository-manifest-and-lock.md), [ADR-054](docs/adr/ADR-054-repository-aggregates-and-manifest.md).
