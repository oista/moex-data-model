# CHANGELOG: Mapping identity slots (ADR-044)

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
