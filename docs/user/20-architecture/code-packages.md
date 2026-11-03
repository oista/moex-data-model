---
id: code-packages
sources:
  - docs/adr/ADR-008-linkml-map-provider.md
  - docs/adr/ADR-017-external-specification-source-sync.md
  - Makefile
  - packages/modeling-kernel/README.md
  - packages/standard-linkml/README.md
  - packages/standard-owl/README.md
  - packages/ontology/README.md
  - packages/specification-dams/README.md
  - packages/repository-loader/README.md
  - packages/publication/README.md
  - packages/semantic-mappings/README.md
  - packages/linkml-tooling/README.md
  - packages/git-adapter/README.md
  - packages/external-sources/README.md
  - packages/ontology-catalog/README.md
  - packages/drawdb-adapter/README.md
draft: true
---

# Пакеты кода

Пакет кода — каталог Python в `packages/`. Это не [пакет модели](glossary:model-package): пакет модели лежит в `model-assets/` и описывает данные. Пакет кода читает, проверяет или собирает такие файлы. Граница нужна, чтобы язык записи, правила DAMS и сборка просмотра не смешивались в одном месте.

Ядро и языки. `modeling-kernel` держит общие типы ролей и порты. Тела языка LinkML сюда не кладут. `standard-linkml` читает YAML и отдаёт его остальным. `standard-owl` читает OWL и RDF. `ontology` оставлен тонкой обёрткой над `standard-owl`, чтобы старые импорты Python находили тот же код.

Правила и состав репозитория. `specification-dams` выполняет правила DAMS и собирает отчёт о соответствии. Сами сущности он из YAML не переписывает. `repository-loader` читает опись `model-assets/implementations/manifest.yaml` и файл фиксации. Фиксацию он не обновляет: это делает команда `moex-model lock update`. Проверка этих двух каталогов входит в общую проверку шагом `dams-packages-check`.

Просмотр и преобразования. `publication` собирает данные, из которых `apps/viewer` делает HTML. `semantic-mappings` готовит проекции глоссария и наборы соответствий между сводами. [Отображение](glossary:mapping) внутри одного решения DAMS живёт отдельно, в пакете модели. `linkml-tooling` подключает библиотеку преобразований `linkml-map`. Остальной код вызывает общий вход ядра `MappingProvider`, а библиотеку напрямую не импортирует (ADR-008). Выражения в преобразованиях по умолчанию выключены.

Стыки наружу. `git-adapter` читает опубликованные файлы в Git через порт, а не через типы конкретного хоста. `external-sources` умеет забирать чужие файлы спецификаций. Решение об этом ещё не принято ([ADR-017](docs/adr/ADR-017-external-specification-source-sync.md)), поэтому этот каталог не считают устройством продукта. `ontology-catalog` складывает выпуски онтологий в пересобираемую базу для просмотра. Источником онтологии эта база не является. `drawdb-adapter` переводит пакет модели в DBML и обратно. Его проверка — цель `make drawdb-adapter-check`, в общую проверку она не входит.

Отдельная цель `make packages-check` гоняет OWL, каталог онтологий и преобразования. В `make check` её нет.

Правило про порт преобразований записано в [ADR-008](docs/adr/ADR-008-linkml-map-provider.md).
