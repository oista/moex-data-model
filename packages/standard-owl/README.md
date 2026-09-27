# MOEX Standard OWL

OWL/RDF provider for the MOEX data model platform: offline parsing, FIBO definition
export, and adapters used by the Ontology Catalog.

**Architecture:** [docs/architecture/ontology-catalog.md](../../docs/architecture/ontology-catalog.md).  
Answers *how to read OWL*. Entity cataloguing lives in `packages/ontology-catalog`.

## Install

```bash
cd packages/standard-owl
pip install -e ".[dev]"
```

Optional OAK (Ontology Access Kit) adapter:

```bash
pip install -e ".[oak]"
```

## FIBO export

```bash
python -m moex_standard_owl.fibo \
  --source ./fibo \
  --output ./output \
  --release master_2026Q2
```

Compatibility entry point: `python -m ontology.fibo` from `packages/ontology`.

## Tests

```bash
pytest -v
```

Uses `tests/fixtures/mini_fibo/` (no full FIBO clone required).
