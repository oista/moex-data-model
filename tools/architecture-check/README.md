# architecture-check

Mechanical guards for the architecture pack under `docs/architecture/`.

## What it checks

1. **kernel_policy** — if `modeling-kernel.yaml` sets
   `extension_policy: standard-specific-bodies-live-in-provider-schemas`,
   no class/slot/enum may use provider-specific prefixes (`LinkML*`, `OpenAPI*`, `OWL*`, …).
2. **doc_consistency** — exactly one `docs/architecture/*.md` has `normative: true`
   frontmatter; that document must mention the DAMS schema `tree_root`
   (`MOEXModelRepository`).

## Run

Requires Python 3.11+.

```bash
# from repo root
python -m pip install -e "./tools/architecture-check[dev]"
python -m pytest tools/architecture-check/tests -q
python -m architecture_check.cli --root .

# or
make architecture-check
```

On Windows without `make`, use the three commands above (set `PYTHON` / `py -3.14` if default `python` is older than 3.11).
