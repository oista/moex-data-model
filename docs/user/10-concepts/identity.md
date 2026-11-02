---
id: identity
sources:
  - docs/architecture/identity-map.md
  - docs/adr/ADR-042-integrity-digest-revisions.md
  - docs/adr/ADR-051-dams-schema-compatibility.md
  - docs/adr/ADR-052-identity-and-versioning.md
verified_at: 2026-11-02
---

# Версии и отпечаток

У модели пять разных «кто это», и их нельзя подменять друг другом.

Смысл элемента — устойчивый идентификатор предмета, не файл и не коммит. Сама работа — ряд версий одного пакета или структуры, без номера версии в имени. [Версия модели](glossary:model-version) — опубликованный номер вида 1.2.0. [Редакция модели](glossary:model-revision) — конкретный снимок содержания: коммит Git или хэш фиксации. [Поставка](glossary:distribution) — конкретный файл, который отдали читателю: путь, тип и его собственный хэш. Время сборки личностью не является.

Отдельно от номера версии есть [отпечаток состава](glossary:integrity-digest). Он отвечает на вопрос, изменилось ли содержание, даже если номер версии ещё не трогали.

Номер схемы DAMS — это контракт самой спецификации, не версия пакета mdm. Он живёт по своим правилам совместимости. Поле `api_version` на пакете легко прочитать как версию HTTP-интерфейса. Сейчас это метка версии спецификации DAMS, например `dams.moex/v0.1`. Переименование поля ещё не сделано.

Где прочитать решение: [ADR-042](docs/adr/ADR-042-integrity-digest-revisions.md), [ADR-051](docs/adr/ADR-051-dams-schema-compatibility.md), [ADR-052](docs/adr/ADR-052-identity-and-versioning.md). Карта вопросов «что изменилось» — [identity-map.md](docs/architecture/identity-map.md).
