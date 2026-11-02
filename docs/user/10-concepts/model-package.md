---
id: model-package
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
  - docs/adr/ADR-054-repository-aggregates-and-manifest.md
verified_at: 2026-11-02
---

# Пакет и репозиторий моделей

Конкретную модель данных пишут как [модельный пакет](glossary:model-package). Это документ реализации: понятийные и логические сущности и техническое описание. Пакет бывает двух уровней. Общая модель предприятия задаёт смысл. Модель решения на неё опирается. Отдельного «логического пакета» нет.

Несколько пакетов вместе образуют [репозиторий моделей](glossary:model-repository). Его не хранят одним гигантским файлом, который кто-то правит целиком. На проверке он собирается из документов пакетов.

Чтобы сборка знала, какие документы входят в репозиторий, рядом лежит [опись состава](glossary:repository-manifest): `model-assets/implementations/manifest.yaml`. Её правят руками, когда документ добавляют, убирают или переносят. Рядом [фиксация состава](glossary:repository-lock) — файл `manifest.lock`. Его пишет только команда обновления фиксации. Проверка этот файл не переписывает.

Где прочитать решение: [ADR-047](docs/adr/ADR-047-repository-manifest-and-lock.md), [ADR-054](docs/adr/ADR-054-repository-aggregates-and-manifest.md).
