# Follow-up: TechnicalAsset viewer tree by `parent_ref`

**Status:** open (does not block phase 2)  
**Date:** 2026-10-05  
**Related:** ADR-031 (registry), ADR-033 (quantum boundary)

## Finding

Viewer / publication today:

- Entity hierarchy uses `parent_concept_ref` (`hierarchy_projection.py`), not TechnicalAsset `parent_ref`.
- Publication packages expose `data_carriers` / `access_points` / `data_containers` / `execution_assets` as flat collections in the vertical slice.
- No grouping of technical assets by `parent_ref` in `publish.yaml` section builders or viewer normalizers (grep: no `parent_ref` under `packages/publication`).

## Proposed task (separate PR, estimate > 1–2 files)

1. Extend publication projection to emit a `technical_asset_tree` (or section graph) from `parent_ref` edges across the four collections.
2. Viewer: render parent → children for assets (reuse hierarchy_graph patterns if possible).
3. Test: fixture ModelPackage with two nesting levels → tree present under `dist` / slice JSON.

Out of scope for phase 1 tails: schema changes.
