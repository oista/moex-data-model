# moex-repository-loader

Read-only loader for `model-assets/implementations/manifest.yaml` and
`manifest.lock` (ADR-047 / P1).

- Does **not** write the lock (CLI `moex-model lock update` owns that).
- Hash mismatch raises; never auto-repairs.
- Lazy: `load_package(id)` reads only that document's files.

Schema source of truth:
`model-assets/specifications/moex-repository-manifest/0.1/schemas/moex-repository-manifest.yaml`.
