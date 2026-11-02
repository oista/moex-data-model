---
id: external-ontologies
sources:
  - docs/architecture/MODELING_ARCHITECTURE.md
  - docs/adr/ADR-014-fibo-profile-metamodel.md
verified_at: 2026-11-02
---

# Внешние онтологии

Чужой свод понятий подключают как [внешнюю спецификацию](glossary:external-specification), а не как ещё одну модель MOEX. Сейчас так подключён [FIBO](glossary:fibo). Профиль говорит, как устроены онтологии FIBO, и лежит в `model-assets/specifications/moex-fibo-profile/0.1/`: вход — `specification.yaml`, состав доменов — `metamodel/fibo-architecture.yaml`. Сами предметные классы вроде «юридическое лицо» в этот профиль не входят. Их место — содержание реализации, а не тело спецификации.

Три соседних решения ещё не приняты. Не закончена загрузка внешнего источника (ADR-017). Не закончено оформление прикладной онтологии как реализации (ADR-018). Не закончен отбор отдельных терминов из внешнего свода (ADR-020). Пока на эти три шага опираться нельзя: работает профиль FIBO как спецификация.

Где прочитать решение: [ADR-014](docs/adr/ADR-014-fibo-profile-metamodel.md).
