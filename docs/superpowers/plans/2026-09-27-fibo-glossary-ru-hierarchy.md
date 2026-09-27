# FIBO glossary RU + hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement inline task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Curated Russian labels/definitions on FIBO preview glossary cards, plus a separate `tree` section built from `parent_local_name` (asserted `rdfs:subClassOf` within the preview set).

**Architecture:** One preview CSV gains `label_ru`, `definition_ru`, `parent_local_name`. Glossary UI shows `label (label_ru)` + EN/RU definitions. CSV normalizer, when `section.type == "tree"`, nests items by `parent_local_name` (same idea as LinkML `is_a` trees). `publish.yaml` adds a hierarchy section pointing at the same CSV.

**Tech Stack:** Python CSV normalizer, Pydantic publication models, vanilla JS glossary/tree renderers, pytest.

**Spec:** `docs/superpowers/specs/2026-09-27-fibo-glossary-ru-hierarchy-design.md`

## Global Constraints

- RU and parents are curated preview-only; do not change full-mart export schema.
- Leave `label_ru` / `definition_ru` empty rather than invent jargon.
- Parents must exist in the same CSV or the row is a root.
- No new section types; reuse `glossary` + `tree`.

---

### Task 1: CSV → tree helper + normalizer

**Files:**
- Modify: `viewer/src/moex_publication_viewer/normalizers/helpers.py`
- Modify: `viewer/src/moex_publication_viewer/normalizers/csv_normalizer.py`
- Test: `viewer/tests/test_normalizers.py`

- [ ] Failing test: CSV with `parent_local_name` + `type: tree` nests child under parent; unknown parent → root
- [ ] Implement `items_to_tree(items, parent_attr="parent_local_name")` and call from `CsvNormalizer` when `section.type == "tree"`
- [ ] pytest green

### Task 2: Curate preview CSV

**Files:**
- Modify: `packages/ontology/publications/fibo_glossary.preview.csv`

- [ ] Add columns `label_ru`, `definition_ru`, `parent_local_name`
- [ ] Fill careful RU for all ~50 rows
- [ ] Set parents only where both ends are in the sample (credit-event / CDS / functional-entity / ABS clusters)

### Task 3: Manifest + glossary UI

**Files:**
- Modify: `packages/ontology/publish.yaml`
- Modify: `viewer/static/viewer.js` (`renderGlossary`)
- Modify: `viewer/tests/test_build.py` (smoke asserts)

- [ ] Add `hierarchy` tree section
- [ ] Glossary card: `label (label_ru)`; EN def + muted RU def; search matches RU fields
- [ ] Golden build asserts RU sample string + fibo tree section

### Task 4: Rebuild + verify

- [ ] `python -m pytest viewer/tests -q`
- [ ] `python -m moex_publication_viewer.cli build --root .`
