# MOEX Ontology Catalog

Registers ontology releases, indexes entities/relations into a rebuildable SQLite
projection, and exposes read models for Publication Viewer.

**Architecture:** [docs/architecture/ontology-catalog.md](../../docs/architecture/ontology-catalog.md).

## Install

```bash
cd packages/standard-owl && pip install -e ".[dev]"
cd ../ontology-catalog && pip install -e ".[dev]"
```

## Rebuild index (mini_fibo / local FIBO)

```bash
python -m moex_ontology.cli rebuild \
  --descriptors ../../model_src/ontologies \
  --source ../../packages/standard-owl/tests/fixtures/mini_fibo \
  --db ./.data/ontology_index.sqlite \
  --preview-out ./publications
```

## Tests

```bash
pytest -v
```
