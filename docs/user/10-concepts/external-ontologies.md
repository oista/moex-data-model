---
id: external-ontologies
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-014-fibo-profile-metamodel.md
  - docs/adr/ADR-017-external-specification-source-sync.md
  - docs/adr/ADR-018-ontology-application-implementation.md
  - docs/adr/ADR-020-external-specification-scope-and-term-selection.md
draft: true
---

# Внешние онтологии

Чужой свод понятий подключают как [внешнюю спецификацию](glossary:external-specification), а не как ещё одну модель MOEX. Сейчас так подключён [FIBO](glossary:fibo). [Профиль внешней спецификации](glossary:external-profile) говорит, как устроены онтологии FIBO, и лежит в `model-assets/specifications/moex-fibo-profile/0.1/`: вход — `specification.yaml`, состав доменов — `metamodel/fibo-architecture.yaml` (ADR-014). Сами предметные классы вроде «юридическое лицо» в этот профиль не входят. Их место — содержание реализации, а не тело спецификации.

Три соседних решения ещё не приняты. Не закончена загрузка внешнего источника (ADR-017). Не закончено оформление прикладной онтологии как реализации (ADR-018). Не закончен отбор отдельных терминов из внешнего свода (ADR-020). Пока на эти три шага опираться нельзя: работает профиль FIBO как спецификация.

Где прочитать решение: [ADR-014](docs/adr/ADR-014-fibo-profile-metamodel.md).
