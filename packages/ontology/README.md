# MOEX Ontology Package

Thin compatibility shim over [`packages/standard-owl`](../standard-owl).  
`python -m ontology.fibo` and `from ontology…` imports keep working; OWL parsing and FIBO export live in `moex_standard_owl`.

**Architecture:** Ontology Catalog is documented in
[`docs/architecture/ontology-catalog.md`](../../docs/architecture/ontology-catalog.md).  
Platform canon: [`MODELING_ARCHITECTURE.md`](../../docs/architecture/MODELING_ARCHITECTURE.md).

## Requirements

- Python 3.11+
- Editable install of sibling `packages/standard-owl` (see Install)

## Install

```bash
cd packages/standard-owl
pip install -e ".[dev]"
cd ../ontology
pip install -e ".[dev]"
```

## Obtain FIBO sources (once)

```bash
git clone --branch master_2026Q2 --depth 1 https://github.com/edmcouncil/fibo.git
```

Processing does not require network access.

## Export definitions

```bash
python -m ontology.fibo \
  --source ./fibo \
  --output ./output \
  --release master_2026Q2
```

Same CLI options as before (`--domains`, `--types`, `--format`, …). Implementation: `moex_standard_owl.fibo`.

## Tests

```bash
pytest -v
```

Tests use `tests/fixtures/mini_fibo/` and do not require a full FIBO clone.

## Upstream

https://github.com/edmcouncil/fibo
