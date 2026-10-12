# P1 inventory: repository manifest (top-level only)

**Date:** 2026-10-12  
**Scope:** inventory for ADR-047 / P1 series (manifest + lock + loader).  
**Out of scope:** splitting large `ModelPackage` bodies (possible later series P1b).

## Finding: no mega-document instance

`MOEXModelRepository` is the LinkML `tree_root` in
[`moex-dams.yaml`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml)
and `root_type` in the DAMS specification envelope. No YAML under
`model-assets/implementations/` materializes it: there is no top-level
`model_packages`, `data_flows`, `data_model_bindings`,
`classification_assignments`, or `policy_bindings` collection in data.

What exists today is **eight** `SpecificationImplementation` envelopes
(`implementation.yaml`) each pointing at a body file. Bodies are validated
as `ModelPackage` (or ontology application body for FIBO), not as
`MOEXModelRepository`. Discovery is a filesystem `rglob` of
`implementation.yaml`.

P1 therefore introduces an addressable **repository index** over those
envelopes, not a migration of a single mega YAML.

## Implementations (8)

| id | Envelope path | Body | Body size (KiB) | Notes |
|---|---|---|---:|---|
| `moex:implementation:moex-enterprise-conceptual-model:0.1` | `enterprise/moex-enterprise-conceptual-model/0.1/` | `enterprise-conceptual-model.yaml` | 124.3 | Enterprise conceptual SoT |
| `moex:implementation:esed:0.1.0` | `solutions/esed/` | `esed-solution-model.yaml` | 105.1 | Solution; depends on enterprise conceptual |
| `moex:implementation:crm:0.1.0` | `solutions/crm/` | `crm-solution-model.yaml` | 65.0 | Solution; depends on enterprise conceptual |
| `moex:implementation:moex-hierarchy:0.1` | `enterprise/moex-hierarchy/` | `moex-hierarchy-model.yaml` | 64.9 | Hierarchy view; `content_digest` is placeholder `sha256:preview-moex-hierarchy` |
| `moex:implementation:mdm:0.1.0` | `solutions/mdm/` | `mdm-solution-model.yaml` | 59.0 | Solution; depends on enterprise conceptual |
| `moex:implementation:ucd:0.1.0` | `solutions/ucd/` | `ucd-solution-model.yaml` | 57.4 | Solution; depends on enterprise conceptual |
| `moex:implementation:client-accounts-csv-draft:0.1` | `imports/client-accounts-csv-draft/0.1/` | `draft-model.yaml` | 2.5 | Draft import |
| `moex:implementation:moex-fibo-application:0.1` | `ontologies/moex-fibo-application/0.1/` | `ontology-application.yaml` | 0.6 | Ontology application body (not ModelPackage shape) |

Sizes measured 2026-10-12 on current tree (UTF-8 file length / 1024).

### Top-level body keys (ModelPackage-shaped)

Shared pattern on CRM / ESED / MDM / UCD:

`element_id`, `name`, `title`, `description`, `lifecycle_status`, `api_version`,
`model_version`, `solution_ref`, `domain_contexts`, `logical_entities`,
`relationships`, `implementation_scope`, `conceptual_implementation_ref`,
`data_owner_ref`, `ownership_inheritance_rule`, `data_carriers`,
`value_domains`, `data_structures`, `field_mappings`,
`entity_physical_mappings`, `realizes_mappings`.

Enterprise conceptual: conceptual collections (`conceptual_entities`,
`relation_terms`, `data_types`, `aligns_with_mappings`) instead of solution
physical/mapping stacks.

Hierarchy: `conceptual_entities` + `logical_entities` + `relationships`.

Draft import: subset of solution keys without `conceptual_implementation_ref`.

FIBO application: different keys (`namespace_iri`, `seed_ref`, module refs).

## Cross-document references (stable ids)

| From | Field | To |
|---|---|---|
| crm / esed / mdm / ucd bodies | `conceptual_implementation_ref` | `moex:implementation:moex-enterprise-conceptual-model:0.1` |

Paths are not used for inter-package links; loaders resolve by
implementation id / slug. Envelope `body_ref` is a path relative to the
envelope directory only.

`data_owner_ref` values in solution bodies are governance placeholders
(`org:role/DATA_OWNER_PENDING`), not code owners for CODEOWNERS / manifest
`owner`.

## Consumers of implementations today

| Consumer | How it finds implementations | Notes for P1 |
|---|---|---|
| CLI `FilesystemImplementationCatalog` ([`asset_registry.py`](../../apps/cli/src/moex_model_cli/asset_registry.py)) | `model-assets/implementations/**/implementation.yaml` via `rglob` | PR-5 switches discovery to loader |
| Viewer [`discovery.py`](../../apps/viewer/src/moex_publication_viewer/discovery.py) | `rglob("publish.yaml")` under repo root | Unchanged in P1; paths stay put |
| API [`app.py`](../../apps/api/src/moex_model_api/app.py) | Uses `FilesystemImplementationCatalog` | Indirectly benefits from PR-5 |
| DAMS assess / repository | Resolve body via CLI bootstrap / catalog | Unchanged until later |
| Digest gate [`digest.py`](../../packages/specification-dams/src/moex_dams/application/digest.py) | `rglob("*.yaml")` under implementations + examples; only instances with `integrity_digest`+`selections` or `data_model_bindings` items | See co-existence below |
| Publication build | Reads body + `publish.yaml` relative to implementation dir | Paths unchanged → publish parity |

## Files outside the future manifest (allow-list)

These are **not** DocumentRef entries. Orphan checks must allow them:

- `**/publish.yaml` — publication module descriptors
- `**/publications/**` — generated / committed publication artifacts
- `solutions/solution-xlsx.profile.yaml` — import profile, not an implementation
- `ontologies/{application,corporate,fibo,moex-data,moex-hr,prov-o}.yaml` — ontology catalog stubs under `implementations/ontologies/` (no `implementation.yaml` sibling for each)
- `enterprise/moex-hierarchy/moex-dams-full.yaml` — flattened schema snapshot for viewer, not a package body
- Sibling YAML next to bodies that are not the `body_ref` (e.g. enterprise conceptual `controlled-vocabularies.yaml`, `data-types.yaml`, `relation-terms.yaml`) — package-local assets referenced by body or docs; remain beside the package

Future files introduced by P1:

- `model-assets/implementations/manifest.yaml` — hand-edited index
- `model-assets/implementations/manifest.lock` — generated JSON Lines (`.lock`, not `*.yaml`)

## Co-existence: `manifest.yaml` vs current scanners

| Scanner | Behavior with `manifest.yaml` in `implementations/` |
|---|---|
| `asset_registry` `rglob(ENVELOPE_NAME)` where `ENVELOPE_NAME == "implementation.yaml"` | Ignores `manifest.yaml` (name filter). |
| `digest.py` `rglob("*.yaml")` | Will open `manifest.yaml`; skips unless it looks like a binding document (`integrity_digest`+`selections` or nested `data_model_bindings`). RepositoryManifest shape does not match → no-op. |
| Viewer `rglob("publish.yaml")` | Unaffected. |

`manifest.lock` uses extension `.lock` so it never enters the digest YAML walk.

## Integrity stamps (three mechanisms)

Documented so P1 lock does not invent a fourth algorithm by accident:

1. **`DataModelBinding.integrity_digest` (ADR-042)** — canonical JSON over binding body, skipping `integrity_digest` and `generated_at`. Implemented in `moex_dams.application.digest`. Checked by digest CLI / publish-gate.
2. **`implementation.yaml` `content_digest` / `revision`** — sha256 of **raw body bytes** at import time (`standard-linkml` envelope helpers). Not verified in CI today; hierarchy uses a placeholder digest.
3. **P1 `manifest.lock` `content_hash` (ADR-047)** — same *canonical JSON* idea as ADR-042 over `{descriptor_without_stamps, body}` (see ADR). Stamps `content_digest`/`revision` are excluded from the hash to avoid a lock ↔ stamp cycle. Stamps are left in place for this series; removal is deferred.

## Baseline for publish parity

No new golden harness for P1. After each PR:

- `make compare-golden`
- `make publish-gate` (or Stage 0 `scripts/check_all.py`)
- `make architecture-check`

Publication paths and body contents are not moved in this series, so
byte-level publish drift is not expected. Schema-derived `generated/**`
must remain untouched when the LinkML manifest module is added as a
**separate** specification tree (see ADR-047 placement rules).

## Boundaries vs existing registries

| Concept | Level | ADR / schema |
|---|---|---|
| `TechnicalAsset` (+ collections on `ModelPackage`) | Data quanta **inside** a package | ADR-031 |
| `RegistryEntry` / ITSystem / … | Local projections of external master data | `moex-registries.yaml` |
| `DocumentRef` / `RepositoryManifest` | Index of **files** (implementations) in the git tree | ADR-047 (P1) |
| `ModelElement` mixins / identity | Class hierarchy inside DAMS | ADR-044 (Proposed) |

Manifest classes stay outside `ModelElement`. Manifest `owner` is a code /
review handle (`@org/team`), not `data_owner_ref` (ADR-023).

## Deferred (not in this inventory’s acceptance)

Splitting large ModelPackage files; flow/contract/assignment document kinds;
CODEOWNERS generation; GitProvider-backed reads; deleting envelope stamps;
viewer/API full loader migration; validating the assembled
`MOEXModelRepository` instance for id collisions.
