# Changelog: retire Group C from active catalog (ADR-056 PR-9)

**Date:** 2026-10-28  
**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md)  
**Branches:** `feat/viewer-hide-inactive-requirements` (PR-9a), `feat/requirements-backbone-pr9-retire-group-c` (PR-9b)

## Summary

Group C (31 rows) leaves the **active** requirements catalog: rows are
`lifecycle_status: deprecated`, not deleted. Enforcement stays in LinkML schema,
Python rules, and constraint-matrix INV. Viewer hides inactive statuses by default.

Physical deletion of deprecated/superseded rows and matrix `requirement_refs`
cleanup is **PR-10**.

## PR-9a — viewer

- Setting `requirements.show_inactive` (default `false`) in
  [`apps/viewer/config/display.yaml`](../../apps/viewer/config/display.yaml).
- Sidebar filter in `filterExplorerItemsForPrefs` drops
  `deprecated` / `superseded` / `rejected` requirement nodes and empty section
  folders; recounts `requirement_count`. Search / deep links still open hidden
  items.

## PR-9b — enforcement + deprecate

### INV-065…067 (re-homed runner conditionals)

| INV | Former check | Validator |
|---|---|---|
| INV-065 | PDM-001.c5 `pdm001_structure_ref` | `technical_assets.check_carrier_structure_ref` |
| INV-066 | PDM-002.c2 `pdm002_scalar_type` | `data_structure.check_scalar_node_type` |
| INV-067 | PDM-002.c3 `pdm002_scalar_required` | `data_structure.check_scalar_node_required` |

Aliases: `DAMS-REQ-PDM-001.c5`, `DAMS-REQ-PDM-002.c2`, `DAMS-REQ-PDM-002.c3`.

### Deprecated catalog codes (31)

**IT-solution (25):** PDM-001, PDM-002, PDM-005…PDM-020, ATR-001, ATR-006, REF-001,
FLW-002…FLW-005.

**Conceptual (6):** CM-GEN-001, CM-GEN-002, CM-REF-001, CM-CON-003, CM-PDM-000,
CM-PROP-001.

`description` on each row points at the enforcement home. Catalog size remains
74. `check_references` is also invoked from `check_formal_requirements` so
`DAMS-REF-005/006` still fire after REF-001 deprecation.

## Not in PR-9

- Deleting rows / rewriting 25 matrix `requirement_refs`.
- Dropping `requirement_code=` / renaming `DAMS-REQ-PDM-009.c3`.
- Group D, Group B recode, GEN-003, glossary wording (PR-10).
