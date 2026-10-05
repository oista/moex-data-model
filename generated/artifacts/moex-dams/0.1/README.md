# DAMS 0.1 generated artifacts

| File | Role |
|------|------|
| `moex-dams.schema.json` | Regenerable JSON Schema (`compare-golden`) |
| `moex-dams.owl.ttl` | Regenerable OWL (`make generate-artifacts`) |
| `moex-dams.shacl.ttl` | Regenerable SHACL |
| `moex-dams.dbml` | Regenerable LinkML `gen-dbml` output (golden) |
| `moex-dams-drawdb-colored.dbml` | **Curated** drawDB sample with header colors — **not** in `compare-golden` |
| `diagrams/*.md` | Regenerable Mermaid class diagrams |
| `python/moex_dams.py` | Regenerable gen-python |
| `docs/` | Regenerable gen-doc — **git:** only `index.md` + `README.md`; full tree after `make generate-artifacts` |
| `moex-dams.rdf.ttl` | Regenerable gen-rdf |
| `ontology-profile.json` | Stage 8 URI/prefix report (`compare-golden` + release bundle) |
| `ontology-profile.md` | Human-readable summary of the same report |

Regenerate: `make generate-artifacts` or `moex-model compile --artifacts`.
