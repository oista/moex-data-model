# FIBO glossary: Russian preview + class hierarchy

**Status:** draft for review  
**Date:** 2026-09-27  
**Project:** moex-data-model

## Problem

The FIBO publication module shows a flat English-only glossary from
`packages/ontology/publications/fibo_glossary.preview.csv` (~50 terms).
Readers need:

1. Careful Russian term (in parentheses) and Russian definition on glossary cards.
2. A native FIBO asserted hierarchy (`rdfs:subClassOf`) as a separate tree section.

Full FIBO mart / RDF pipeline stays out of scope. Preview remains a curated,
committed CSV updated via PR.

## Decisions (approved)

| Topic | Choice |
|-------|--------|
| Russian source | **A** — curated translations in preview CSV only |
| Hierarchy UX | **A** — separate `tree` section beside the glossary |
| Data shape | **1** — one CSV with `label_ru`, `definition_ru`, `parent_local_name` |

## Data model (preview CSV)

Add columns (UTF-8):

| Column | Role |
|--------|------|
| `label_ru` | Russian term; optional but preferred for all preview rows |
| `definition_ru` | Russian definition; optional; omit rather than invent if unsure |
| `parent_local_name` | Parent class `local_name` if that parent is **also in this CSV**; else empty (root in the preview tree) |

Existing English columns (`label`, `definition`, …) stay authoritative.

**Translation rules (careful):**

- Prefer established finance/ontology Russian where stable (e.g. cash flow → денежный поток).
- Do not invent FIBO-specific jargon; if no good RU term, leave `label_ru` empty rather than guess.
- Definitions: short faithful paraphrase of EN, not a new normative meaning.
- Mark nothing as “official FIBO Russian” — curation is MOEX preview only.

**Hierarchy rules:**

- `parent_local_name` mirrors asserted `rdfs:subClassOf` among classes present in the preview set only.
- Parents outside the preview sample are not materialized; child becomes a root of the preview tree.
- Example chains that fit the current sample:  
  `FailureToPayInterest` → `FailureToPay` → `DefaultEvent` → `CreditEvent`  
  (and similar credit-event / ABS clusters where both ends exist in CSV).

## Viewer behaviour

### Glossary section

- Title line: `label (label_ru)` when `label_ru` is non-empty; else `label` only.
- Body: English definition; if `definition_ru` present, show it below as a second paragraph (muted or lightly marked as RU — keep visual quiet).
- Local search filter also matches `label_ru` and `definition_ru`.

### Tree section (new)

In `packages/ontology/publish.yaml`:

- `id: hierarchy` (or similar)
- `type: tree`
- same CSV path
- `key_column: local_name`

CSV normalizer (when `section.type == "tree"`): build nested `PublicationItem.children` from `parent_local_name` (same pattern as LinkML `is_a` tree). Rows with missing/unknown parent are roots. Sort children by id/title.

Reuse existing `renderTree` UI; no new section type.

## Out of scope

- Extracting RU or hierarchy from live FIBO RDF / full export.
- Changing full-mart CSV schema under `output/`.
- SSSOM / ontology-catalog packages.
- Making group/package nodes selectable (unrelated to this work).

## Acceptance

1. Glossary cards show `EN (RU)` and RU definition when columns filled.
2. FIBO module has a collapsible class hierarchy tree built from `parent_local_name`.
3. `make viewer-check` / existing pytest green; golden build still finds three modules including fibo.
4. Preview CSV remains the single curated source for both sections.

## Test notes

- Unit: CSV → tree attaches child under parent when `parent_local_name` set; orphan parent id → root.
- Smoke: rebuilt HTML contains a Russian sample string and `"type": "tree"` (or tree section id) for fibo.
