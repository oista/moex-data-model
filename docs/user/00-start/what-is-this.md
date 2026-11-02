---
id: what-is-this
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-010-owl-not-primary-validation.md
  - docs/adr/ADR-028-package-documentation-section.md
  - docs/adr/ADR-057-user-documentation.md
  - docs/adr/ADR-003-postgres-operational.md
draft: true
---

# Что это за продукт

Это репозиторий, в котором лежат правила описания данных MOEX и конкретные модели, собранные по этим правилам.

Он нужен архитектору, который впервые открывает проект, и агенту, которому надо понять, что сейчас правда. Здесь три роли: [стандарт моделирования](glossary:modeling-standard), [спецификация](glossary:reference-specification) и [реализация](glossary:specification-implementation). Сейчас это язык LinkML, спецификация DAMS 0.1 и модели вроде пакета mdm.

Сейчас здесь можно править файлы модели в YAML, прогнать проверки командами репозитория и открыть [публикацию](glossary:publication) — собранный просмотр.

Этот текст описывает продукт как он есть и новых правил не задаёт. Принятые решения остаются в `docs/adr/`. Чертёж связей систем живёт во внешней системе, а здесь хранят привязку смысла к нему. [Операционное хранилище](glossary:operational-store) для черновиков и поиска файлы модели в Git не заменяет. Сделать такой базой PostgreSQL предложено в [ADR-003](docs/adr/ADR-003-postgres-operational.md), и это решение ещё не принято. Модель не проверяют через OWL. Этот просмотр — про продукт целиком, а не документация одного пакета: отдельный раздел документации у пакета ещё не принят (ADR-028).
