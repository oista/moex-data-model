# moex.dsp — Data Specification Player metamodel

**moex.dsp** описывает метамодель самого **Data Specification Player**: как эталонные
спецификации, их реализации и модули публикации проецируются для чтения.

Это не корпоративная модель данных MOEX и не онтология FIBO. Пакет живёт под
**moex.dams** как связанная публикация: плеер читает артефакты DAMS (и других
пакетов), а `moex.dsp` фиксирует понятия самой оболочки публикации.

Норматив по видам разделов и профилям: [ADR-016](../../../docs/adr/ADR-016-publication-section-kinds-and-profiles.md).

## Что описывает

| Понятие | Роль |
|---|---|
| Architecture catalog | Дерево головных спецификаций и вложенных реализаций в боковой панели |
| Reference specification | Эталонный пакет (`moex.dams`, `edmc.fibo`, …) |
| Specification implementation | Публикация, согласованная с эталоном (в т.ч. сам `moex.dsp`) |
| Publication module | Открытый набор экземпляров разделов; `profile` выбирает ProfileSpec |
| Publication section | Экземпляр раздела: `kind` (семантика) + `type` (render/wire) |
| PublicationSectionKind | Закрытый словарь: overview, classes, taxonomy, glossary, … |
| Publication profile | `linkml-specification` \| `ontology` \| `implementation` |
| Publication item | Класс, термин или иной элемент внутри раздела |

## Kind vs type

- **`kind`** (`PublicationSectionKind`) — семантика раздела (ADR-016).
- **`type`** (manifest `SectionKind` render) — формат представления: `explorer`, `glossary`, `markdown-doc`, …
- Один kind `classes` + разные renderer modes от profile: `data-structure` (LinkML) vs `ontology-list` (ontology).
- Kind **`taxonomy`** — отдельный; primary nav для онтологий; **forbidden** на `linkml-specification`.

## Профили (ProfileSpec)

| Profile | Required | Recommended | Forbidden |
|---|---|---|---|
| `linkml-specification` | overview, classes, schema-files | enumerations, slots | taxonomy |
| `ontology` | overview, taxonomy, glossary | classes, identity | schema-files, enumerations, slots |
| `implementation` | overview, conformance | bindings, data-flows | taxonomy |

## Разделы этого модуля

1. **Overview** — этот документ.
2. **Classes** — типизированная иерархия классов LinkML-метамодели плеера.
3. **Glossary** — определения терминов без сугубо технических деталей реализации.

## Связь с другими пакетами

- **moex.dams** — эталонная спецификация модели данных (`profile: linkml-specification`); `moex.dsp` вложен под неё в навигации.
- **edmc.fibo** — эталонный профиль FIBO (`profile: ontology`); primary nav = taxonomy.
