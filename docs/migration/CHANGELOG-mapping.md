# CHANGELOG: Mapping identity slots (ADR-044) and typed collections (ADR-046)

## 2026-10-12 — Typed collections + legacy removal — schema **3.1.0** (ADR-046 PR-5)

- Removed polymorphic `ModelPackage.mappings` slot (use typed collections only):
  `realizes_mappings`, `entity_physical_mappings`, `field_mappings`,
  `aligns_with_mappings`.
- Removed unused `MappingTypeEnum` values: `semantic_equivalence`,
  `specialization`, `implementation`, `transformation`, `aggregation`,
  `derivation`. Kept: `entity_physical`, `field_mapping`, `realizes`,
  `aligns_with`.
- Base class `Mapping` retained as inheritance root for typed subclasses.
- `iter_mappings()` reads typed collections only (legacy key ignored).
- Schema package version: **3.0.0** → **3.1.0**.

## 2026-10-06 — Deprecation — schema **2.1.0** (PR-3)

- `Mapping` no longer redeclares `valid_from` / `valid_to` (via `HasLifecycle` → `HasValidity`).
- On `Mapping` via `slot_usage`:
  - `name` — **optional** + deprecated (Pydantic `Optional[str]`). Prefer
    `source_refs -> target_refs [mapping_type]`.
  - `title`, `aliases`, `glossary_term_refs`, `tags` — deprecated.
  - `description` — optional.
- Existing instance `name` values remain valid.
- Viewer: `mapping_display_label()`; report:
  `scripts/migrate_mapping_labels.py --report`.
- Removal → schema **3.0.0** (PR-6).

## 2026-10-06 — Removal — schema **3.0.0** (PR-6)

- `Mapping` is now `is_a: IdentifiedElement` with mixins
  `DescribedElement`, `HasLifecycle`, `HasProvenance` (no longer `ModelElement` /
  `NamedElement` / `HasSemanticAnnotations`).
- Removed identity slots from Mapping: `name`, `title`, `aliases`,
  `glossary_term_refs`, `tags`.
- Instance data: `scripts/migrate_mapping_labels.py --strip-deprecated`
  (ruamel); display label remains `source_refs -> target_refs [mapping_type]`.
