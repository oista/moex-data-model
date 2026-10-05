---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-030: DAMS URI and prefix policy

**Date:** 2026-10-05  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «Ontology Engine»  
**Related:** [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-011](ADR-011-reproducible-artifacts.md), [ontology-catalog.md](../architecture/ontology-catalog.md)

## Context

Stage 6 already regenerates OWL / RDF / SHACL from DAMS LinkML. Without a URI and prefix policy, IRI drift and prefix conflicts make external alignment (FIBO, catalogs, SSSOM) fragile. Stage 8 closes that gap: stable IRIs, merged prefix registry, schema lint, URI semantic diff, ontology profile report, and SHACL checks for RDF instances.

## Decision

### Base and IRI shapes

- Base namespace: `https://data.moex.com/dams/` (`prefixes.dams`, `default_prefix: dams`).
- Class IRI = `{dams}{ClassName}`.
- Slot IRI = `{dams}{slot_name}`.
- Enum IRI = `{dams}{EnumName}`.
- Permissible value IRI = `{enumIRI}#{value}` (as emitted by current `owlgen`).

### Explicit `class_uri` / `slot_uri`

Do **not** set `class_uri` / `slot_uri` on DAMS metamodel classes. Those fields are reserved for alignment to an *external* ontology. Absence on DAMS schemas is intentional.

### Prefix registry

The registry is the **merged** `SchemaView` prefix map of the root DAMS schema and all imports — not a separate JSON file.

- One prefix key → one URI across all imports.
- Prefix URI values must end with `/` or `#`.

### Breaking changes

Changing any of the following is **breaking**:

- `default_prefix`
- a `prefixes.*` URI value
- a class / slot / enum / permissible-value local name that changes its expanded IRI
- an explicit `class_uri` / `slot_uri` / `meaning`

`MOEX-ID-001` continues to apply to *instance* identifiers (ModelPackage), not schema element IRIs. Schema IRI changes are reported as `MOEX-ONT-010` via schema URI semantic diff.

### Validation boundaries (ADR-010)

- YAML / JSON instances: LinkML validation + DAMS rules.
- RDF instances: SHACL / pySHACL (optional `ontology` extra; `RDFLibDumper` → shapes).
- OWL: derived publication artifact, not a YAML validity gate.
- `linkml-owl`: optional experimental instance export script; not in Stage 0 golden / publish gate.

### OWL mapping (document current `owlgen`)

- Mixins: `owl:Class` with consumers linked via `rdfs:subClassOf`.
- Enum permissible values: `owl:Class` (not `owl:NamedIndividual`). Do not switch `owlgen` representation in this stage.

### Spike result (2026-10-05)

`linkml_runtime.dumpers.rdflib_dumper.RDFLibDumper` dump of a minimal `ModelPackage` **conforms** to committed `moex-dams.shacl.ttl` under pySHACL (`inference=none`). Fixture path: dump from YAML via dumper (go).

## Consequences

- Schema lint codes `MOEX-ONT-001`…`004` and URI diff `MOEX-ONT-010`.
- Regenerable `ontology-profile.json` in golden + release bundle.
- `make ontology-check` (extra deps) validates RDF instance fixtures; Stage 0 `make check` stays free of `pyshacl` / `linkml-owl`.

## Alternatives

| Alternative | Why not |
|---|---|
| Separate prefix JSON | Duplicates LinkML source of truth |
| Explicit `class_uri` on every DAMS class | Noisy; IRIs already derive from `default_prefix` |
| Enum as NamedIndividual | Would change golden OWL without consumer need |
| OWL reasoner as YAML gate | ADR-010 |

## Related

- ADR-001, ADR-010, ADR-011, ontology-catalog.md, IMPLEMENTATION_PLAN § этап 8
