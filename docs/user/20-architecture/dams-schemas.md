---
id: dams-schemas
sources:
  - docs/adr/ADR-043-transitional-tags-registry.md
  - docs/adr/ADR-044-model-element-decomposition.md
  - docs/adr/ADR-050-containment-parent-refs.md
  - docs/adr/ADR-053-qualified-assertion.md
  - model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-base.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-governance.yaml
draft: true
---

# Как устроены схемы DAMS

Схема DAMS — это описание классов и полей, по которому пишут пакеты модели. Файлы лежат в `model-assets/specifications/moex-dams/0.1/schemas/`. Корень — `moex-dams.yaml`: в нём номер версии схемы и список подключаемых файлов. Слои модели на этой странице не разбираются: они описаны в главе «Ключевые идеи».

Рядом с корнем лежат такие файлы. `moex-types.yaml` задаёт общие типы, в том числе номер версии. `moex-registries.yaml` описывает локальную проекцию чужого справочника. `moex-base.yaml` собирает общие наборы полей элемента. `moex-governance.yaml` описывает назначения. `moex-core.yaml` — сущности и отображения. `moex-semantic.yaml` — смысл списка значений. `moex-datatypes.yaml` — типы данных. `moex-technical.yaml` — технические объекты. `moex-structure.yaml` — структуры, узлы и сообщения. `moex-integration.yaml` — потоки данных. `moex-contract-binding.yaml` — привязку модели к контракту. `moex-analytics.yaml` — показатели. `moex-requirements.yaml` — где требование применимо.

Общий класс элемента разобран на наборы полей в `moex-base.yaml` (ADR-044). У элемента с глобальным номером есть набор `IdentifiedElement`. Описание больше не требуется на каждом классе. У отображения срок действия берётся из общего набора, а не объявляется второй раз.

Утверждение о соответствии, ссылка на внешний класс, определение в контексте и назначение несут одни и те же сведения: срок, происхождение и уверенность. Для этого в `moex-governance.yaml` есть набор `HasAssertionMetadata` (ADR-053). Отдельного класса «утверждение» в схеме нет. Ссылка на внешний класс остаётся записью на понятийном элементе. Отображение на уровне пакета может её повторять и не должно ей противоречить.

У вложенного логического атрибута поле `owner_entity_ref`, если оно заполнено, обязано совпасть с `element_id` сущности, внутри которой атрибут лежит. Расхождение — ошибка, код проверки INV-052 (ADR-050). Убирать само поле из YAML пока не стали: это сломало бы уже записанные файлы.

Элемент, который миграция или импорт собрали не до конца, помечают списком `tags` значением `transitional`. Других переходных значений нет. Поле `annotations.transitional` для этого не используют. Метки разделов в `publish.yaml` к этому списку не относятся (ADR-043). Снять метку можно только отдельным изменением данных, после того как идентичность элемента подтверждена.

Где прочитать решения: [ADR-044](docs/adr/ADR-044-model-element-decomposition.md), [ADR-053](docs/adr/ADR-053-qualified-assertion.md), [ADR-050](docs/adr/ADR-050-containment-parent-refs.md). Остальные номера названы выше, рядом со своим смыслом.
