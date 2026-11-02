---
id: source-of-truth
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-001-linkml-yaml-canonical.md
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-011-reproducible-artifacts.md
verified_at: 2026-11-02
---

# Что правят руками

Правят файлы модели в Git. Для DAMS это YAML на языке [LinkML](glossary:linkml). Коммит в Git и есть [опубликованный источник](glossary:published-source): пока изменение не в Git, его нет для остальных.

Всё остальное — [производный файл](glossary:derived-artifact). HTML просмотра, DBML, картинки, OWL и каталог `generated/` собираются из YAML и сами источником не являются. Их можно удалить и получить снова. Приложение drawDB показывает схему, но не хранит модель. OWL-файл тоже не тот механизм, которым модель проверяют.

Операционная база и файловое хранилище могут держать черновики, задачи и уже собранные файлы. Опубликованные файлы в Git они не заменяют.

Где прочитать решение: [ADR-001](docs/adr/ADR-001-linkml-yaml-canonical.md), [ADR-002](docs/adr/ADR-002-git-published-source.md), [ADR-005](docs/adr/ADR-005-drawdb-isolated.md), [ADR-006](docs/adr/ADR-006-dbml-projection.md), [ADR-010](docs/adr/ADR-010-owl-not-primary-validation.md), [ADR-011](docs/adr/ADR-011-reproducible-artifacts.md).
