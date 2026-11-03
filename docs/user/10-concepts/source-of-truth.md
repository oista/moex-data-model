---
id: source-of-truth
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-001-linkml-yaml-canonical.md
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-011-reproducible-artifacts.md
  - docs/adr/ADR-003-postgres-operational.md
  - docs/adr/ADR-005-drawdb-isolated.md
  - docs/adr/ADR-006-dbml-projection.md
  - docs/adr/ADR-010-owl-not-primary-validation.md
draft: true
---

# Что правят руками

Правят файлы модели в Git. Для DAMS это YAML на языке [LinkML](glossary:linkml) (ADR-001). Коммит в Git и есть [опубликованный источник](glossary:published-source): пока изменение не в Git, его нет для остальных (ADR-002).

Всё остальное — [производный файл](glossary:derived-artifact). HTML просмотра, DBML, картинки, OWL и каталог `generated/` собираются из YAML и сами источником не являются (ADR-011). Их можно удалить и получить снова. DBML — проекция схемы, а не место, где правят модель (ADR-006). Приложение drawDB показывает схему, но не хранит модель (ADR-005). OWL-файл тоже не тот механизм, которым модель проверяют (ADR-010).

Черновики, задачи и поиск по уже собранным файлам можно держать в [операционном хранилище](glossary:operational-store). Сделать такой базой PostgreSQL предложено в [ADR-003](docs/adr/ADR-003-postgres-operational.md). Это решение ещё не принято, поэтому база сейчас не устройство продукта. Опубликованные файлы модели остаются в Git.

Где прочитать решение: [ADR-001](docs/adr/ADR-001-linkml-yaml-canonical.md), [ADR-002](docs/adr/ADR-002-git-published-source.md), [ADR-011](docs/adr/ADR-011-reproducible-artifacts.md). Остальные номера названы выше, рядом со своим смыслом.
