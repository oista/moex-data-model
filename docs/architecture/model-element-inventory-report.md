---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ModelElement inventory report (ADR-044, PR-0)

**Date:** 2026-10-06  
**Schema:** `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` (`version: 2.0.0`)  
**Matrix:** [model-element-matrix-before.csv](model-element-matrix-before.csv) / [model-element-matrix-before.md](model-element-matrix-before.md)  
**ADR:** [ADR-044](../adr/ADR-044-model-element-decomposition.md)  
**Spike script:** `tmp/spike_model_element_mixins.py` (not committed as production code)

Schema **not** changed in this PR. Branch stacked on `chore/adr-renumber-phase1-tail` (ADR-042 / ADR-043).

## 1. Schemas inventoried (13 modules under `0.1/schemas/`)

| Module | Role in inventory |
|---|---|
| `moex-dams` | tree root `MOEXModelRepository` |
| `moex-core` | `ModelElement`, conceptual/logical, Mapping, ExternalClassRef |
| `moex-governance` | lifecycle / ownership / definition mixins; ClassificationAssignment, PolicyBinding, ScopedDefinition |
| `moex-structure` | EmbeddedElement, DataStructure, SchemaNode, Message |
| `moex-technical` | TechnicalAsset hierarchy |
| `moex-semantic` | ConceptualDomain, ValueMeaning |
| `moex-datatypes` | DataType, ValueDomain, NativeTypeBinding, PermissibleValue, ValueSetQuery |
| `moex-registries` | RegistryEntry family |
| `moex-integration` | DataFlow, DataFlowEntityBinding |
| `moex-contract-binding` | DataModelBinding, ModelSelection, SelectedEntity, SelectedAttribute |
| `moex-analytics` | Metric, Dimension |
| `moex-requirements` | SpecificationRequirement (+ FormalCheck, RequirementApplicability, RequirementCatalog) |
| `moex-types` | shared types / enums (no ModelElement classes) |

`ExternalTermSelection` lives in **moex-external-alignment** (DSP), not in DAMS schemas — out of DAMS ModelElement scope; noted only.

## 2. Spike results (a)–(e) — LinkML 1.11.1

| Id | Check | Result |
|---|---|---|
| **(a)** | `slot_usage` on `HasDefinition` with `mixins: [DescribedElement]` applies to `LogicalEntity` (5 mixins); linkml-lint clean | **OK** — `induced.required=false`, description text and `exact_mappings: [skos:definition]` induced |
| **(b)** | `slot_uri` vs `exact_mappings` in OWL | **OK / informational** — `induced.slot_uri` stays null; OWL still emits `dams:description`; `skos:definition` from `exact_mappings` does **not** appear as predicate. Confirms ADR-044: no `slot_uri` change in PR-1; SKOS via OWL transform |
| **(c)** | `deprecated` + `required: false` on `Mapping.name` via `slot_usage` | **OK** — JSON Schema drops `name` from `required`; property remains; pydantic text mentions deprecated |
| **(d)** | `recommended: true` on description | **OK** — gen-pydantic / gen-json-schema do not crash; `induced.recommended=true` |
| **(e)** | Pydantic MRO for `ModelElement = IdentifiedElement + 4 mixins` | **OK** — `class ModelElement(HasLifecycle, HasSemanticAnnotations, DescribedElement, NamedElement, IdentifiedElement)` |

**Stop condition:** no LinkML behaviour blocked PR-1. Proceed with `HasDefinition: mixins: [DescribedElement]` + `slot_usage` (no `slot_uri`).

## 3. Classes with proprietary identifier (do **not** become IdentifiedElement)

| Class | Identifier slot | Proposed role (PR-4 / PR-6) |
|---|---|---|
| ClassificationAssignment | `assignment_id` | none + HasValidity (+ keep HasProvenance fields via approval_status) |
| PolicyBinding | `policy_binding_id` | none + HasValidity |
| ScopedDefinition | `scoped_definition_id` | none + HasProvenance (already) |
| ExternalClassRef | `external_class_ref_id` | none + HasProvenance (already) |
| ValueMeaning | `meaning_key` | **exception** — keep own id; do not rename to `local_key`; optional HasProvenance later; not EmbeddedElement without data migration |
| NativeTypeBinding | `binding_id` | none (service binding) |
| PermissibleValue | `value_code` | none / embedded-like |
| ValueSetQuery | `value_set_query_id` | none |
| FormalCheck | `check_id` | none |
| RequirementApplicability | `applicability_id` | none |
| RequirementCatalog | `catalog_id` | none (+ own `name`) |
| RegistryEntry (+ all subclasses) | `registry_id` | stay RegistryEntry; never IdentifiedElement |
| MOEXModelRepository | `repository_id` | tree root; exception allowlist |
| EmbeddedElement / SchemaNode | `local_key` | EmbeddedElement (+ DescribedElement in PR-2) |

## 4. Class → current role → proposal

### ModelElement descendants (keep ModelElement unless noted)

| Class | Notes / proposal |
|---|---|
| ModelElement | Redefine via IdentifiedElement + Named/Described/HasLifecycle/HasSemanticAnnotations |
| ModelPackage, DomainContext | Keep; `description` stays **required** |
| ConceptualEntity, ConceptualProperty, LogicalEntity, LogicalAttribute, RelationTerm | Keep; drop local description slot_usage (move to HasDefinition) |
| Relationship | Keep ModelElement; **soften description** (D4) |
| Mapping | Keep ModelElement until 3.0.0; then IdentifiedElement + HasProvenance + HasLifecycle; deprecate name/title/aliases/tags/glossary_term_refs in 2.1.0; soften name+description |
| Message | Keep; drop description slot_usage (optional stays via DescribedElement) |
| DataStructure | Keep; description → recommended (not required) |
| TechnicalAsset, DataCarrier, AccessPoint, DataContainer, ExecutionAsset | Keep; description stays required (TechnicalAsset slot_usage) |
| ConceptualDomain, DataType, ValueDomain | Keep; description stays required (invariant) until separate decision |
| DataFlow, DataFlowEntityBinding | Keep; remove duplicate `HasLifecycle` mixin on DataFlow (PR-4); description required (invariant) |
| DataModelBinding | Keep; remove duplicate `HasLifecycle` (PR-4) |
| ModelSelection, SelectedEntity, SelectedAttribute | Keep ModelElement for now (have element_id); revisit if they should be IdentifiedElement-only without NamedElement |
| Metric, Dimension, SpecificationRequirement | Keep; description required (invariant) |

### EmbeddedElement

| Class | Proposal |
|---|---|
| EmbeddedElement | `mixins: [DescribedElement]`; drop own description + slot_usage |
| SchemaNode | inherits; drop redundant `slot_usage.description` |

### none (service / registry)

See §3 — HasValidity where `valid_from`/`valid_to` already exist (ClassificationAssignment, PolicyBinding); no IdentifiedElement.

## 5. Allowlist: `slot_usage.description` after PR-1

Classes that currently have explicit `slot_usage.description` or that must retain `required: true` after global `description` becomes optional:

| Class | After PR-1 | Reason |
|---|---|---|
| HasDefinition | **keep** (canonical) | shared softened definition text + exact_mappings skos:definition |
| ModelPackage | **add** `required: true` | D1 |
| DomainContext | **add** `required: true` | D1 |
| TechnicalAsset | **keep** `required: true` | invariant (CDE / quantum) |
| ConceptualDomain | **add** `required: true` | preserve pre-ADR-044 required |
| DataType | **add** `required: true` | preserve |
| ValueDomain | **add** `required: true` | preserve |
| DataFlow | **add** `required: true` | preserve |
| DataFlowEntityBinding | **add** `required: true` | preserve |
| DataModelBinding | **add** `required: true` | preserve |
| ModelSelection | **add** `required: true` | preserve |
| SelectedEntity | **add** `required: true` | preserve |
| SelectedAttribute | **add** `required: true` | preserve |
| Metric | **add** `required: true` | preserve |
| Dimension | **add** `required: true` | preserve |
| SpecificationRequirement | **add** `required: true` | preserve |
| DataStructure | **add** `recommended: true` (not required) | D1 |
| Relationship | **none** — global optional only (no class slot_usage) | D4; confirmed |
| Mapping | **none** in PR-1/PR-2 (global optional); PR-3 adds deprecated slot_usage | D3 |
| ConceptualEntity, ConceptualProperty, LogicalEntity, LogicalAttribute, RelationTerm, Message | **remove** local copy | moved to HasDefinition |
| SchemaNode / EmbeddedElement | **remove** in PR-2 | DescribedElement |

List must not grow without an ADR-044 amendment. Architecture-check (PR-2) enforces this allowlist.

## 6. Python / consumer grep (summary)

| Area | Finding |
|---|---|
| `apps/api` `ModelElementIndex` | Indexes `element_id` + `name` — Mapping.name deprecation needs viewer/API label fallback (PR-3) |
| `packages/specification-dams` `rules/cascade.py`, `definitions.py` | ADR-023 / ADR-025 resolvers — unaffected by mixin reshape if induced slots stay |
| `apps/viewer` glossary / hierarchy | Uses `definition_source_ref` + `description`; optional description already handled |
| `scripts/migrate_*` | Pattern for PR-3 mapping label migration |
| Implementations | Many `mappings:` blocks (ucd, crm, mdm, drafts) with `mapping_type`; Mapping `name` present on elements — inventory for migrate script in PR-3 |

## 7. Golden / fixtures touched by later PRs

- `generated/contracts/moex-dams/0.1/**` (Pydantic MRO / bases will change; field sets+required must match — PR-1 acceptance)
- `generated/artifacts/moex-dams/0.1/moex-dams.schema.json` (canonical key-sort byte-equal — PR-1)
- `generated/artifacts/moex-dams/0.1/python/moex_dams.py` (MRO diff documented per class, not auto-accepted)
- `generated/artifacts/moex-dams/0.1/{owl,shacl,rdf,doc,mermaid,dbml}` as regenerated
- `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` (must include `moex-base` after PR-1)
- Solution models under `model-assets/implementations/solutions/**` (Mapping.name optional from PR-3)

## 8. PR notes (non-blocking)

1. Duplicate ADR-034 / ADR-035 numbering is fixed on branch `chore/adr-renumber-phase1-tail` → ADR-042 / ADR-043; this PR depends on that branch.
2. Accepted ADR-038 / ADR-040 / ADR-041 (and ADR index frontmatter) still have `superseded_by: MODELING_ARCHITECTURE.md`; incorrect for Accepted — track separately.
3. Schema version path: **2.1.0** in PR-1, **3.0.0** in PR-6 (catalogue `0.1/` kept).
