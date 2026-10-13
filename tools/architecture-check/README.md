# architecture-check

Mechanical guards for the architecture pack under `docs/architecture/` and DAMS schema hygiene (ADR-044).

## What it checks

1. **kernel_policy** — if `modeling-kernel.yaml` sets
   `extension_policy: standard-specific-bodies-live-in-provider-schemas`,
   no class/slot/enum may use provider-specific prefixes (`LinkML*`, `OpenAPI*`, `OWL*`, …).
2. **doc_consistency** — exactly one `docs/architecture/*.md` has `normative: true`
   frontmatter; that document must mention the DAMS schema `tree_root`
   (`MOEXModelRepository`).
3. **layer_boundaries** — conceptual→physical reference direction rules for DAMS classes.
4. **model_element_roles** — single `description` slot home (`moex-base.yaml`);
   `slot_usage.description` only on ADR-044 allowlist classes; allowlist keys must
   appear in ADR-044 § Description slot_usage allowlist; IdentifiedElement and
   EmbeddedElement must not share an `is_a` chain.
5. **redundant_mixins** — class must not re-declare a mixin already induced via
   `is_a` parent chain or via another declared sibling mixin (ADR-044).

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

## Growing the description allowlist

1. Amend [ADR-044](../../docs/adr/ADR-044-model-element-decomposition.md) § Description slot_usage allowlist.
2. Add the class key to `DESCRIPTION_SLOT_USAGE_ALLOWLIST` in
   `src/architecture_check/model_element_roles.py` with a short reason.
3. CI fails if either side drifts.
