---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# PR-C3 report: L2 validators (ADR-045)

## Scope

L2 validators for INV-001, INV-010, INV-011, INV-014 and confirmed candidates INV-018…027 with aligned/confirmed sources. Wired through existing `moex_dams/rules/*.py` (assess / architecture-check / publish-gate). No parallel rule system. Real data not auto-fixed.

## Files

| Area | Paths |
|---|---|
| New L2 | `semantic_layer.py` (`check_identifying_requires_is_identifying` / DAMS-INV-001); `data_structure.py` (INV-010/011/014 + tags 012/013/017/019/020/021/022); `technical_assets.py` (INV-015/016/018); `ontology_uris.py` (INV-026 on MOEX-ONT-004) |
| Tests | `packages/specification-dams/tests/test_invariant_l2.py` |
| Matrix | `constraint-matrix.yaml` (levels/status/notes/dams_validator) |
| Docs | this report; ADR-045 §Open questions; changelog C3 |

## Source discipline

| ID | source_status | C3 action |
|---|---|---|
| INV-001 | aligned | L2 enforces (L1 boolean defect unchanged) |
| INV-010 | partial | L2 bound to slot text only |
| INV-011 | divergent | L2 mirrors LinkML; AsyncAPI question unchanged (ADR-045) |
| INV-014 | partial | L2 bound to slot text only |
| INV-017 | partial | L2 only for `message_refs` ban on interface |
| INV-018…022, 026 | aligned | tagged / confirmed existing validators |
| INV-023/024/027 | partial | **skipped** (no invented norm) |
| INV-025 | aligned | **skipped** — no package-instance tags validator found |

## check_all

| Interpreter | Result |
|---|---|
| 3.12.10 (`apps/cli/.venv`) | OK (all 9 steps) |
| 3.14.4 (temporary `apps/cli/.venv`, then restored 3.12) | OK (all 9 steps) |

Logs under `tmp/check_all_c3_py312.log` / `tmp/check_all_c3_py314.log` (gitignored).

## Newly invalid real data

Scan (L2 only, codes `DAMS-INV-001/010/011/014`) over `model-assets/implementations/**/*.yaml` (excluding schema dump `moex-dams-full.yaml`) and DAMS examples (excluding `examples/invariants/`):

**0 hits.** No package became newly invalid under the new L2 codes. Pre-existing PDM diagnostics (retagged with `invariant_id` only) are not counted as new.

## Decision options if new failures appear later

1. Fix the data.
2. Weaken the rule (with matrix/ADR update).
3. Waiver with ADR reference.

## History hygiene (pre-C3)

Misleading log commits `e146390` / `120013c` removed from C2 history (rebuild + force-with-lease). Local `tmp/**/*check_all*.log` ignored; logs are not published artifacts.
