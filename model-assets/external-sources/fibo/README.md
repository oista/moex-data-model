# External source: FIBO (modular extract)

Pinned **module extracts** of the EDM Council FIBO ontology used by MOEX mappings —
not a full FIBO vendor tree (ADR-017).

## Layout

| Path | Role |
|---|---|
| `registry.yaml` | Upstream metadata, adapter=`fibo`, ROBOT pin |
| `seeds/moex-core.txt` | Default combined IRI list for sync |
| `seeds/counterparty.txt` | LegalPerson (SSSOM / Client mapping) |
| `seeds/business-dates.txt` | BusinessDay (profile FND slice) |
| `modules/*.ttl` | ROBOT / fallback extract output (committed) |
| `lockfile.yaml` | Pinned upstream_ref + content/seed hashes |

## Relation to scopes and selections (ADR-020)

Version pin metadata: [`versions/2026Q2/`](versions/2026Q2/).
Governance search boundaries and term selections live under
[`external-scopes/`](../../external-scopes/) and
[`external-selections/`](../../external-selections/) — not in this sync tree.

## Relation to `moex-fibo-profile`

[`model-assets/specifications/moex-fibo-profile`](../../specifications/moex-fibo-profile) is the
**ReferenceSpecification** metamodel (ADR-014). This tree is the **upstream release mirror
materialization** that feeds Impl/catalog content later — sync does **not** auto-publish.

Test upstream currently points at
`packages/external-sources/tests/fixtures/mini_ontology` (LegalPerson + BusinessDay + parents).

## Sync

```powershell
moex-model source sync fibo
moex-model source diff fibo
# optional single seed:
moex-model source sync fibo --seed model-assets/external-sources/fibo/seeds/counterparty.txt
```

ROBOT: set `ROBOT_JAR` to a pinned jar, or place `robot-1.9.5.jar` under `.cache/robot/`.
Without ROBOT, the adapter falls back to a BOT-like Turtle closure (test/dev only).
