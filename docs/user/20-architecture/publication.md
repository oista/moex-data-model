---
id: publication-view
sources:
  - docs/adr/ADR-015-viewer-ui-atlas.md
  - docs/adr/ADR-016-publication-section-kinds-and-profiles.md
  - docs/adr/ADR-019-publication-contract-inheritance.md
  - model-assets/specifications/moex-dams/0.1/publish.yaml
  - model-assets/specifications/moex-dsp/0.1/schemas/moex-dsp.yaml
  - apps/viewer/src/moex_publication_viewer/validators.py
  - apps/viewer/src/moex_publication_viewer/build.py
draft: true
---

# Публикация и просмотр

[Публикация](glossary:publication) модели собирается из файла `publish.yaml`, который лежит рядом с пакетом. У спецификации DAMS это `model-assets/specifications/moex-dams/0.1/publish.yaml`. У реализации пример — `model-assets/implementations/solutions/mdm/publish.yaml`. В файле перечислены модули и разделы: что показать и откуда взять данные. Сборка — `make viewer`. Результат — статический HTML, его руками не правят.

У модуля есть вид публикации, поле `profile`. Видов три. `linkml-specification` — спецификация на LinkML: обязательны обзор, классы и файлы схемы. `ontology` — онтология: обязательны обзор, классы и глоссарий. `implementation` — реализация: обязательны обзор и отчёт о соответствии. У раздела есть роль, поле `kind`: обзор, классы, слоты, глоссарий и другие значения из закрытого списка. Список живёт в схеме `model-assets/specifications/moex-dsp/0.1/schemas/moex-dsp.yaml`. Роль раздела и способ отрисовки — разные поля. Один и тот же `kind: classes` на спецификации LinkML рисуется таблицей, на онтологии — списком классов.

Если обязательной роли нет или стоит запрещённая, сборка пишет предупреждение и не останавливается (ADR-016). Для спецификации на LinkML запрещена роль таксономии: отдельное дерево классов сверх списка классов. Для онтологии запрещены роли перечислений и слотов.

Реализация, которая заявляет соответствие спецификации, наследует обязательства публикации, а не имена её модулей. У раздела реализации поле `satisfies` перечисляет, какие обязательства он закрывает. Имена, порядок и группировка разделов могут отличаться от спецификации. Сборка просмотра это проверяет: обязательство без раздела сборку останавливает (ADR-019).

Оформление просмотра задано отдельно (ADR-015). Это дерево слева, карточка объекта и цвета MOEX. Макет лежит в `docs/design/viewer-atlas/`. Оформление модель не меняет. Этот текст про продукт собран той же оболочкой, но его манифест — `docs/user/user-docs.yaml`, и правила `publish.yaml` на него не распространяются.

Где прочитать решения: [ADR-016](docs/adr/ADR-016-publication-section-kinds-and-profiles.md), [ADR-019](docs/adr/ADR-019-publication-contract-inheritance.md), [ADR-015](docs/adr/ADR-015-viewer-ui-atlas.md).
