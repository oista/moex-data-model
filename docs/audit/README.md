# Architect audits

Source material for architectural reviews of the DAMS object model.

| Artifact | Notes |
|---|---|
| `2026-10-01-Architect audit DAMS Object Model.docx` | Original audit. Binary is gitignored (`docs/audit/*.docx`); keep locally or attach outside git. |
| Closure review plan | `.cursor/plans/` — `moex-data-model: Audit closure review` (Save to Workspace), waves A–F. |
| [ADR-055](../adr/ADR-055-integration-source-of-truth.md) | Wave F: Integration SoT + remap of audit 0.2 integration criteria. |
| [P2-BACKLOG.md](../migration/P2-BACKLOG.md) | Deferred P2 items and ADR follow-ups (docs only until a series starts). |
| [TRAIN-6.0.0.md](../migration/TRAIN-6.0.0.md) | Residual P1 schema train: entry criteria G1–G6, work packages T6-1…T6-8, pre-train minors M-1…M-5. |
| [identity-map.md](../architecture/identity-map.md) | Wave D2 follow-up: question → field → where (Version ≠ Revision ≠ Distribution). |
| [ADR-052](../adr/ADR-052-identity-and-versioning.md) | Five-layer identity; operational Distribution record (D6/D7); `api_version` rename deferred to 6.0.0. |

P0/P1 close-out status lives in ADRs 031–054 on `main`. Wave F (ADR-055) records that protocol-neutral exchange / adapters are consciously deferred to P2, not left as open defects against ADR-048.

**Version identity (audit P1):** closed at contract/tooling level (operational manifests, publish-gate, identity-map). Schema-level residual items are tracked as explicit train tasks in [TRAIN-6.0.0.md](../migration/TRAIN-6.0.0.md) (not as open bugs); index row [P2-BACKLOG F0-3](../migration/P2-BACKLOG.md).
