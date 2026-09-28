# External source: FIBO (modular extract)

Pinned **module extracts** of the EDM Council FIBO ontology used by MOEX mappings —
not a full FIBO vendor tree (ADR-017).

## Layout

| Path | Role |
|---|---|
| `registry.yaml` | Upstream metadata, adapter=`fibo`, ROBOT pin |
| `seeds/*.txt` | IRI term lists (one IRI per line) |
| `modules/*.ttl` | ROBOT extract output (committed) |
| `lockfile.yaml` | Pinned upstream_ref + content/seed hashes |

## Relation to `moex-fibo-profile`

[`model-assets/specifications/moex-fibo-profile`](../../specifications/moex-fibo-profile) is the
**ReferenceSpecification** metamodel (ADR-014). This tree is the **upstream release mirror
materialization** that feeds Impl/catalog content later — sync does **not** auto-publish.

## Sync

```powershell
# Point registry.yaml upstream_url at a local FIBO checkout or mini fixture, then:
moex-model source sync fibo
moex-model source diff fibo
```

ROBOT: set `ROBOT_JAR` to a pinned jar, or place `robot-1.9.5.jar` under `.cache/robot/`.
Without ROBOT, the adapter falls back to a test-only line filter (not for production pins).

## Seeds

`seeds/counterparty.txt` currently lists IRIs referenced from
`model-assets/transformations/mappings/dams-fibo.sssom.yaml`.
