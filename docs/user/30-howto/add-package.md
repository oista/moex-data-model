---
id: add-package
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
  - docs/adr/ADR-054-repository-aggregates-and-manifest.md
  - model-assets/implementations/manifest.yaml
  - model-assets/implementations/solutions/mdm/publish.yaml
  - model-assets/specifications/moex-dams/0.1/publish.yaml
  - model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml
  - apps/viewer/src/moex_publication_viewer/discovery.py
draft: true
---

# Добавить спецификацию или реализацию

[Спецификация](glossary:reference-specification) задаёт правила языка для MOEX. [Реализация](glossary:specification-implementation) — уже заполненная модель. Их кладут в разные каталоги. В [опись состава](glossary:repository-manifest) входит только реализация.

Спецификация лежит в `model-assets/specifications/`. У DAMS это `model-assets/specifications/moex-dams/0.1/`. Рядом с ней лежит `publish.yaml`: по этому файлу просмотрщик находит модуль. В `model-assets/implementations/manifest.yaml` спецификацию не вносят.

Реализация — [модельный пакет](glossary:model-package) под `model-assets/implementations/`. Пример решения: `model-assets/implementations/solutions/mdm/`. Чтобы общая проверка его видела, в опись `model-assets/implementations/manifest.yaml` добавляют строку с путём к `implementation.yaml`. Затем `moex-model lock update --root .` переписывает [фиксацию состава](glossary:repository-lock) (ADR-047). Просмотрщик ищет `publish.yaml` рядом с пакетом по этой описи (ADR-054). Место в дереве просмотра задаёт `model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml`. Без записи модуль попадает в собранный HTML, но не появляется в ветке «Реализации».

Где прочитать решение: [ADR-047](docs/adr/ADR-047-repository-manifest-and-lock.md), [ADR-054](docs/adr/ADR-054-repository-aggregates-and-manifest.md).
