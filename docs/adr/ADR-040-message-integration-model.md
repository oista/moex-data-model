---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-040: Message — интеграционная модель

**Date:** 2026-10-06  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-033](ADR-033-technical-asset-quantum-boundary.md), [ADR-038](ADR-038-datastructure-and-schemanode.md), [ADR-031](ADR-031-technical-asset-registry.md)

## Context

В quantum boundary (ADR-033) transitional `payload` / `message` моделировались как `DataCarrier` с `asset_kind: message_type`. Это смешивает **квант носителя** (топик, файл, таблица) с **описанием сообщения** интеграционного контракта. Сообщение не имеет `asset_namespace` / `qualified_name` в смысле TechnicalAsset и не должно попадать в `carrier_refs`.

Нужен отдельный элемент интеграционной модели со ссылками на структуры payload/headers и явной цепочкой AccessPoint → Message → DataStructure.

## Decision

### Message — ModelElement, не TechnicalAsset

- `Message` `is_a: ModelElement` (не `DataCarrier` / не mixin `HasStructure`).
- Нет `asset_namespace` / `qualified_name`; не участвует в `carrier_refs`.
- Структура через `payload_structure_ref` (required) и `headers_structure_ref` (optional) → `DataStructure`.
- Коллекция `messages` на `ModelPackage`.

### Размещение модуля (архитектурный долг-lite)

Целевой дом по смыслу — `moex-integration.yaml`. На практике класс объявлен в **`moex-structure.yaml`**, чтобы `ModelPackage` и `AccessPoint` ссылались на `Message` **без** цикла импортов `core ↔ integration`.

Это **намеренное** размещение (debt-lite): семантически Message — интеграция; схемно — рядом со структурами, от которых зависит. Не закреплять второй цикл `core ↔ structure` как норму. Перенос в `moex-integration` возможен позже, если граф импортов позволит без Conflicting URIs / поломки SchemaView.

### AccessPoint.message_refs

- Слот `message_refs` → `Message` (multivalued, not inlined).
- Допустимо только для `AccessPoint` kind **`operation` | `channel`**.
- Для `interface` (и прочих kinds) — запрет (LinkML rule + DAMS).

### Envelope

- `envelope_kind`: `none` | `cloudevents` | `custom`.
- `envelope_ref` — опциональная ссылка на описание конверта / профиля (для `custom` и именованных профилей).
- Дополнительно: `content_type`, `correlation_hint`.

### Цепочка адресов

```
AccessPoint  --message_refs-->  Message  --payload/headers_structure_ref-->  DataStructure
DataCarrier  --structure_ref-->  DataStructure
```

Носитель (топик и т.п.) остаётся `DataCarrier` со `structure_ref` на структуру; сообщение — отдельный слой контракта, на который указывает точка доступа.

### Миграция legacy `message_type`

`DataCarrier` / kind `message_type` → `Message`; неоднозначный канал AccessPoint — ошибка миграции (в отчёт). Transitional-теги и kind `message_type` уходят в 2.0.0 вместе с удалением PhysicalField-эпохи.

## Consequences

- ADR-033 уточняется: transitional `message_type` как carrier больше не целевая модель.
- Интеграционные контракты адресуются без раздувания реестра TechnicalAsset.
- Размещение Message в `moex-structure` документировано как долг; потребители импортируют structure-модуль.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Message как DataCarrier (`message_type`) | смешивает квант и контракт; ADR-033 transitional — временное |
| Message mixin HasStructure | один structure_ref недостаточен для payload+headers |
| Сразу в moex-integration при цикле импортов | ломает SchemaView / Conflicting URIs |
| message_refs на любом AccessPoint | interface не несёт operation/channel semantics |

## References

- AsyncAPI 3.0 — Message Object / Multi Format Schema
- CloudEvents
- ADR-033 (quantum boundary), ADR-038 (DataStructure), ADR-031 (registry)
