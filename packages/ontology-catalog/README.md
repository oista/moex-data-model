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

From `packages/ontology-catalog`:

```bash
python -m moex_ontology.cli rebuild \
  --descriptors ../../model_src/ontologies \
  --source ../standard-owl/tests/fixtures/mini_fibo \
  --db ./.data/ontology_index.sqlite \
  --preview-out ./publications \
  --sssom ../../model_src/mappings/dams-fibo.sssom.yaml
```

`FND/Broken/Broken.rdf` in the mini fixture is intentional (parse-error tests); rebuild skips it and continues.

## Tests

```bash
pytest -v
```
