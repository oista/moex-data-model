---
name: "moex-data-model: ADR numbering fix"
overview: "На main два ADR-034 и два ADR-035 (коллизия номеров после параллельных PR #7/#8 и #11). Переименовываем phase1-tail ADR в свободные ADR-042/043 как с меньшим «весом» ссылок; DAMS-цепочка 034–041 остаётся без изменений. Один небольшой docs/chore PR без правок схем и generated."
todos:
  - id: branch
    content: "Создать ветку chore/adr-renumber-phase1-tail от актуального main"
    status: completed
  - id: rename-files
    content: "git mv ADR-034-integrity-digest-revisions.md -> ADR-042-...; ADR-035-transitional-tags-registry.md -> ADR-043-... (сохранить историю)"
    status: pending
  - id: fix-adr-bodies
    content: "Поправить заголовки '# ADR-0xx' внутри двух перенесённых ADR и их ссылки на самих себя (ADR-035 -> ADR-043 в тексте реестра)"
    status: pending
  - id: fix-code-refs
    content: "Заменить ADR-034 -> ADR-042 в digest-контексте: __main__.py, commands/digest.py, gates/publish_gate.py, application/digest.py, tests/test_digest.py, Makefile:92"
    status: pending
  - id: fix-tags-refs
    content: "ADR-035 -> ADR-043 в tests/architecture/test_transitional_tags_registry.py (docstring и комментарий-путь) и CONTRIBUTING.md:24"
    status: pending
  - id: readme-index
    content: "docs/adr/README.md: добавить строки ADR-042, ADR-043 (сейчас в индексе их нет вообще)"
    status: pending
  - id: dedupe-guard
    content: "Добавить архитектурный тест на уникальность номеров ADR (docs/adr/ADR-NNN-*.md), чтобы коллизия не повторилась"
    status: pending
  - id: verify
    content: "Проверка: нет дублей номеров, grep-критерий, pytest tests/architecture + specification-dams digest tests, make check-all"
    status: pending
isProject: false
---

# moex-data-model: ADR numbering fix

## Диагноз

В `docs/adr/` коллизия номеров:

| Файл | Попал в main | Коммит |
|---|---|---|
| `ADR-034-integrity-digest-revisions.md` | 12:09 | #7 (phase1-tail) |
| `ADR-035-transitional-tags-registry.md` | 12:15 | #8 (phase1-tail) |
| `ADR-034-lightweight-conceptual-property.md` | 12:47 | #11 (DAMS) |
| `ADR-035-value-domains.md` | 12:47 | #11 (DAMS) |

Причина: ветки `chore/phase1-tail-*` и `feat/data-structure-schema-node` писались параллельно и обе взяли «следующий свободный» номер 034/035. Номера 042+ в репозитории не используются, открытых PR нет, так что переименование ничего не конфликтует.

## Решение: какую пару переименовывать

Переименовываем **phase1-tail** (integrity-digest, transitional-tags), а не DAMS-пару.

Почему:
- DAMS ADR-034/035 — часть связной цепочки 034–041 (взаимные `Related:` у ADR-035/036/037, `ADR-041` ссылается на «ADR-035/037»).
- На них ссылаются ~25 мест в `model-assets/**` (moex-core, moex-datatypes, moex-semantic, requirements, moex-dams-full) и, транзитивно, `generated/**` (owl/shacl/schema.json/python/contracts). Переименование потребовало бы правки схем, регенерации артефактов, пересчёта `integrity_digest` и смены версии.
- phase1-tail ADR цитируются только в коде/Makefile/тестах/CONTRIBUTING (~15 строк), `generated/` не затрагивают.
- Тест `test_attribute_semantics_residue.py` держит allowlist-префикс `docs/adr/ADR-034` для lightweight-ADR — он остаётся валидным.

Новые номера: `ADR-042` — integrity-digest-revisions, `ADR-043` — transitional-tags-registry (сохраняем хронологический порядок #7 → #8).

## Шаги

### 1. Переименование файлов
```
git mv docs/adr/ADR-034-integrity-digest-revisions.md   docs/adr/ADR-042-integrity-digest-revisions.md
git mv docs/adr/ADR-035-transitional-tags-registry.md   docs/adr/ADR-043-transitional-tags-registry.md
```

### 2. Тела ADR
- `ADR-042`: заголовок `# ADR-034: integrity_digest ...` → `# ADR-042: ...`.
- `ADR-043`: заголовок `# ADR-035: ...` → `# ADR-043: ...`; строка 49 «правка ADR-035 + тест allowlist» → `ADR-043`.
- Проверить, что в обоих нет ссылок на ADR-031 и пр., которые нужно менять (не нужно) — менять только самоссылки.

### 3. Ссылки на integrity-digest: ADR-034 → ADR-042
Только эти файлы (все контекстуально про `integrity_digest`):
- `apps/cli/src/moex_model_cli/__main__.py` (стр. 436, 452)
- `apps/cli/src/moex_model_cli/commands/digest.py` (стр. 1, 48)
- `apps/cli/src/moex_model_cli/gates/publish_gate.py` (стр. 213)
- `packages/specification-dams/src/moex_dams/application/digest.py` (стр. 1, 133)
- `packages/specification-dams/tests/test_digest.py` (стр. 1)
- `Makefile` (стр. 92)

**Не трогать** остальные `ADR-034` — они про lightweight ConceptualProperty (model-assets, `concept_coverage.py`, `semantic_layer.py`, residue-тест, `moex-deprecated-slots.yaml`, requirements).

Спорный случай: `tools/architecture-check/.../layer_boundaries.py:1` — «ADR-034 / §5» про layer boundaries. По смыслу не относится ни к одному из двух ADR; выяснить по git blame/контексту и либо оставить, либо заменить на корректный (например ADR-021) отдельным коммитом.

### 4. Ссылки на transitional-tags: ADR-035 → ADR-043
- `tests/architecture/test_transitional_tags_registry.py` (стр. 1 и 13: docstring + путь к файлу)
- `CONTRIBUTING.md` (стр. 24)

**Не трогать** остальные `ADR-035` — они про ConceptualDomain/ValueDomain (model-assets, `value_domain_enum.py`, ADR-034/036/041, README).

### 5. README индекс ADR
В `docs/adr/README.md` после строки ADR-041 добавить `ADR-042` и `ADR-043` (в индексе они сейчас отсутствуют — только DAMS-версии 034/035). Статус обоих — Accepted. Файл в кодировке с кириллицей — править точечно (StrReplace), не перезаписывать целиком.

### 6. Замок от повторения
Новый тест `tests/architecture/test_adr_numbers_unique.py`: собирает `docs/adr/ADR-(\d{3})-*.md`, падает при дубликате номера (с перечнем файлов). Опционально — проверка, что каждый ADR есть в `README.md`. Тест входит в существующий `tests/architecture`, подхватывается `make check-all`.

### 7. Побочное наблюдение (по желанию, отдельно)
Во frontmatter обоих phase1-tail ADR стоит `superseded_by: MODELING_ARCHITECTURE.md` при статусе Accepted — выглядит как артефакт шаблона (у остальных `[]`). Не входит в этот PR; вынести отдельным вопросом.

## Проверка
1. `Get-ChildItem docs/adr | group {$_.Name.Substring(0,7)} | ? Count -gt 1` — пусто.
2. `rg "ADR-034" apps packages Makefile` → только semantic-контекст (lightweight); `rg "ADR-035" tests CONTRIBUTING.md` → пусто для tags-контекста.
3. `rg "integrity-digest-revisions|transitional-tags-registry"` — ссылки только на новые имена файлов.
4. `pytest tests/architecture packages/specification-dams/tests/test_digest.py`, затем `make check-all` (в т.ч. digest-гейт из Makefile:92).
5. `git diff --stat` — не должно быть изменений в `model-assets/**` и `generated/**`.

## Риски
- **Замена «вслепую»** по `ADR-034`/`ADR-035` сломает смысл DAMS-ссылок — править только перечисленные файлы/строки.
- **Исторические ссылки вне репо** (описания PR #7/#8, внешние заметки) продолжат указывать на старые номера — зафиксировать в сообщении коммита: `ADR-034 (integrity-digest) -> ADR-042`, `ADR-035 (transitional-tags) -> ADR-043`.
- **Принятые ADR не переписываются** (CONTRIBUTING): здесь это допустимо, т.к. меняется только номер/имя из-за коллизии, содержание решений не трогается; пометить в коммите как editorial.
