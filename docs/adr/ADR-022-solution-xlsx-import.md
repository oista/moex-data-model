---
status: Accepted
version: "0.1"
date: 2026-10-04
---

# ADR-022: Object/ObjectAttribute xlsx → DAMS solution import

## Context

IT-solution models (MDM, UCD, CRM, ЕСЭД) arrive as a shared workbook with
`Object` / `ObjectAttribute` sheets. Canonical DAMS solution bodies live as
editable YAML under `model-assets/implementations/solutions/{slug}/` (ADR-002,
ADR-021). An existing ER-dictionary ingest already maps neutral sheets to
`ModelPackage` (`moex_standard_linkml.ingest`).

Hard-coding a second full mapper, or putting DAMS assess inside
`standard-linkml`, would either duplicate logic or create a package cycle
(`specification-dams` → `standard-linkml`).

## Decision

1. **Adapter, not a second mapper.** Package
   `moex_standard_linkml.solution_xlsx` reads the MOEX workbook into a
   `SolutionIR`, runs input rules (`SXI-*`), projects to in-memory
   `WorkbookTables`, then calls `map_er_dictionary`. Layout and defaults live
   in a YAML `SolutionXlsxProfile` (header discovery by column names, per-system
   `type_map` / technology / `system_ref`).

2. **Package boundary.** `solution_xlsx` must not import `moex_dams`.
   Orchestration (convert → LinkML validate → assess → export-slice → report)
   lives in `apps/cli` (`import-solution`). Fitness test:
   `tests/architecture/test_import_boundaries.py`.

3. **Canonical YAML.** Generated `{slug}-solution-model.yaml` +
   `implementation.yaml` under `model-assets/implementations/solutions/{slug}/`
   are the edit SoT. Writer never overwrites without `--force`; otherwise
   artifacts go to the report directory (exit 3, `SXI-IO-001`).

4. **Source privacy.** External `--xlsx` path is not stored as `file:///…` in
   envelopes. Persist filename + content sha256 (`source_label`).

5. **Two diagnostic contours.** Input rules `SXI-*` with RU message +
   remediation + sheet/row/column. IT-solution requirements (GEN/LDM/ATR/…)
   stay in `moex_dams.assess_implementation`; CLI merges them into the same
   report via `element_id → SourceRef` trace.

6. **Mode A now, B later.** Target rows only in the model; `src_only` rows kept
   in IR. Profile switch `src_only: ignore | physical` (v1 = `ignore`).

## Consequences

- New CLI: `moex-model import-solution`.
- Working profile at
  `model-assets/implementations/solutions/solution-xlsx.profile.yaml`.
- Roadmap B enables physical fields from src-only without refactoring IR.

## Related

- ADR-002, ADR-004, ADR-009, ADR-013, ADR-019, ADR-021
- [`docs/dev/solution-xlsx-import.md`](../dev/solution-xlsx-import.md)
