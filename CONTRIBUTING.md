# Contributing to moex-data-model

## Pull requests

- Prefer **small, reviewable PRs**. Schema changes and data/instance migrations **must not** share a PR:
  - **Schema PR** — LinkML modules under `model-assets/specifications/`, generated contracts/artifacts (via regen only), ADRs for the schema decision.
  - **Data / migration PR** — solution YAML, examples, `vertical_slice.json`, migration scripts applied to instances, digests/revisions.
- Phase work is sliced the same way (see TechnicalAsset phase 1: schema switch vs consumer/slice follow-ups).
- Commit message prefix for process follow-ups: `chore(phase1-tail):` (or the active phase id).
- Do not hand-edit `generated/**`; regenerate with `scripts/generate-contracts.ps1` / `generate-artifacts.ps1` / `moex-model compile`.

## Checks

Primary entry (Windows-friendly):

```bash
python scripts/check_all.py
```

On Linux/macOS, `make check` delegates to the same script when available; individual Makefile targets remain.

## ADRs

Accepted ADRs are not rewritten for additive registries — add a new ADR (e.g. tags registry ADR-043 after Accepted ADR-031).
