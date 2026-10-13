---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR index (001–055)

**Date:** 2026-10-12  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)

Decisions referenced from [linkml_architecture.md](../architecture/linkml_architecture.md). Each ADR has its own frontmatter `status`. On conflict with an Accepted ADR, the ADR wins over informal architecture notes until MODELING_ARCHITECTURE is updated.

Viewer-specific decisions: [viewer-decisions.md](../architecture/viewer-decisions.md). UI presentation — [ADR-015](ADR-015-viewer-ui-atlas.md) / [viewer-atlas](../design/viewer-atlas/README.md).

| ADR | Title | Status | Scope / schema (on `main`) |
|---|---|---|---|
| [ADR-001](ADR-001-linkml-yaml-canonical.md) | LinkML YAML — канонический authoring format для DAMS | Proposed | canonical authoring |
| [ADR-002](ADR-002-git-published-source.md) | Git — источник опубликованных версий | Proposed | published source |
| [ADR-003](ADR-003-postgres-operational.md) | PostgreSQL — операционное хранилище и поисковая проекция | Proposed | Workbench ops store (no code yet) |
| [ADR-004](ADR-004-modular-monolith.md) | Модульный монолит вместо микросервисов | Proposed | packages + apps |
| [ADR-005](ADR-005-drawdb-isolated.md) | drawDB — изолированное self-hosted приложение | Proposed | apps/drawdb + adapter |
| [ADR-006](ADR-006-dbml-projection.md) | DBML — проекция, а не источник истины | Proposed | projection; Stage 5 MVP |
| [ADR-007](ADR-007-pydantic-dto-not-validator.md) | Pydantic — API DTO, но не единственный validator | Proposed | API DTO pattern |
| [ADR-008](ADR-008-linkml-map-provider.md) | LinkML Map скрывается за provider interface | Accepted | provider interface |
| [ADR-009](ADR-009-schema-automator-draft-only.md) | schema-automator используется только для draft import | Accepted | draft import only |
| [ADR-010](ADR-010-owl-not-primary-validation.md) | OWL не применяется как основной механизм validation | Proposed | OWL not primary validation |
| [ADR-011](ADR-011-reproducible-artifacts.md) | Generated artifacts должны быть воспроизводимыми | Proposed | golden / reproducible artifacts |
| [ADR-012](ADR-012-semantic-diff-review.md) | Все изменения публикуются через semantic diff и review | Proposed | semantic diff / review |
| [ADR-013](ADR-013-specification-requirements-catalog.md) | Каталог требований к спецификации в DAMS LinkML | Proposed | requirements catalog |
| [ADR-014](ADR-014-fibo-profile-metamodel.md) | FIBO profile — ReferenceSpecification; domain content outside Spec explorer | Proposed | FIBO profile metamodel |
| [ADR-015](ADR-015-viewer-ui-atlas.md) | MOEX Publication Viewer — UI/UX Design Standard (MOEX Atlas) | Proposed | viewer UI atlas |
| [ADR-016](ADR-016-publication-section-kinds-and-profiles.md) | Publication section kinds and profiles | Proposed | publication section kinds |
| [ADR-017](ADR-017-external-specification-source-sync.md) | External specification source sync | Proposed | external source sync |
| [ADR-018](ADR-018-ontology-application-implementation.md) | Ontology SpecificationImplementation = application / extension ontology | Proposed | ontology SpecImpl |
| [ADR-019](ADR-019-publication-contract-inheritance.md) | Publication contract inheritance | Proposed | publication contract inheritance |
| [ADR-020](ADR-020-external-specification-scope-and-term-selection.md) | External Specification Scope and Term Selection | Proposed | scope vs import |
| [ADR-021](ADR-021-dams-implementation-profile-and-levels.md) | DAMS-specific implementation profile and model levels | Proposed | dams-data-model levels |
| [ADR-022](ADR-022-solution-xlsx-import.md) | Object/ObjectAttribute xlsx → DAMS solution import | Accepted | solution_xlsx import |
| [ADR-023](ADR-023-governed-property-cascade.md) | Containment cascade of governed properties | Proposed | governed property cascade |
| [ADR-024](ADR-024-unified-class-entity.md) | Unified Class entity across LinkML and OWL publications | Proposed | unified Class entity |
| [ADR-025](ADR-025-definition-cascade-and-glossary.md) | Definition cascade and glossary terminology | Proposed | definition cascade / glossary |
| [ADR-026](ADR-026-cmd-entity-metamodel.md) | Conceptual entity metamodel (tier, genesis, relation terms) | Proposed | conceptual entity metamodel |
| [ADR-027](ADR-027-glossary-term-relations.md) | Glossary term relations (hierarchy vs associative vs equivalence) | Proposed | glossary term relations |
| [ADR-028](ADR-028-package-documentation-section.md) | Package documentation section | Proposed | package documentation section |
| [ADR-029](ADR-029-cdm-from-er-sketch-and-realization.md) | Conceptualizing ER sketches into CDM; realization completeness (not subclass) | Proposed | ER sketch → CDM; no ConceptualAttribute |
| [ADR-030](ADR-030-dams-uri-and-prefix-policy.md) | DAMS URI and prefix policy | Accepted | URI / prefix policy (Stage 8) |
| [ADR-031](ADR-031-technical-asset-registry.md) | TechnicalAsset as unified registry of data quanta (квант данных) | Accepted | TechnicalAsset registry |
| [ADR-032](ADR-032-technical-asset-identity.md) | TechnicalAsset identity | Accepted | TechnicalAsset identity |
| [ADR-033](ADR-033-technical-asset-quantum-boundary.md) | Quantum boundary | Accepted | quantum boundary |
| [ADR-034](ADR-034-lightweight-conceptual-property.md) | Смысл и представление — облегчённый ConceptualProperty (вариант B) | Accepted | lightweight ConceptualProperty |
| [ADR-035](ADR-035-value-domains.md) | ConceptualDomain и ValueDomain | Accepted | ConceptualDomain / ValueDomain |
| [ADR-036](ADR-036-datatype-system.md) | Типовая система DataType и NativeTypeBinding | Accepted | DataType / NativeTypeBinding |
| [ADR-037](ADR-037-attribute-semantics-migration.md) | Миграция семантики LogicalAttribute | Accepted | LogicalAttribute semantics migration |
| [ADR-038](ADR-038-datastructure-and-schemanode.md) | DataStructure и SchemaNode | Accepted | DataStructure / SchemaNode |
| [ADR-039](ADR-039-structure-node-addressing.md) | Адресация узлов SchemaNode | Accepted | SchemaNode addressing |
| [ADR-040](ADR-040-message-integration-model.md) | Message — интеграционная модель | Accepted | Message integration model |
| [ADR-041](ADR-041-schemanode-datatype-binding.md) | Привязка SchemaNode к DataType / native type | Accepted | SchemaNode ↔ DataType |
| [ADR-042](ADR-042-integrity-digest-revisions.md) | integrity_digest and model revisions for non-demo models | Accepted | integrity_digest / revisions |
| [ADR-043](ADR-043-transitional-tags-registry.md) | Transitional element tags registry | Accepted | transitional tags registry |
| [ADR-044](ADR-044-model-element-decomposition.md) | ModelElement decomposition | Accepted | ModelElement mixins (moex-base) |
| [ADR-045](ADR-045-executable-constraint-matrix.md) | Executable constraint matrix | Accepted | constraint matrix L1/L2/L3 |
| [ADR-046](ADR-046-typed-mapping-endpoints.md) | Typed Mapping endpoints (subclasses + separate collections) | Accepted | typed Mapping collections; schema 3.1.0 |
| [ADR-047](ADR-047-repository-manifest-and-lock.md) | Repository manifest and lock | Accepted | repository manifest + lock |
| [ADR-048](ADR-048-topology-ownership.md) | Topology ownership (Clinkr/EAM SoT, DAMS semantic bindings) | Accepted | topology ownership; schema 4.0.0→4.1.0 |
| [ADR-049](ADR-049-governance-assignment-authority.md) | Governance assignment authority (assignments over cascade; EffectiveGovernanceView) | Accepted | schema 5.0.0; INV-054..056; D9 module split; see governance-inventory.md |
| [ADR-050](ADR-050-containment-parent-refs.md) | Containment parent refs (owner equality / INV-052) | Accepted | containment equality; Wave C3 |
| [ADR-051](ADR-051-dams-schema-compatibility.md) | DAMS schema compatibility (semver + release trains) | Accepted | aggregate semver; timeline; evidence gate |
| [ADR-052](ADR-052-identity-and-versioning.md) | Identity and versioning (five layers) | Accepted | identity map; api_version rename deferred; id_prefixes lint |
| [ADR-053](ADR-053-qualified-assertion.md) | Qualified assertion pattern | Accepted | HasAssertionMetadata in schema 5.1.0; INV-057; Transformation end date |
| [ADR-054](ADR-054-repository-aggregates-and-manifest.md) | Repository aggregates and manifest (P1b) | Accepted | validation composite; package-only DocumentKind; path-scoped orphans; INV-058 global element_id |
| [ADR-055](ADR-055-integration-source-of-truth.md) | Integration source of truth (Clinkr/EAM topology; audit Wave F) | Accepted | Integration SoT; audit 0.2 remap; P2 backlog |

## How to accept

1. Review against [CHECKLIST.md](../architecture/CHECKLIST.md) if the change touches the core.
2. Change frontmatter `status: Proposed` → `Accepted` only after an explicit decision.
3. Do not duplicate §14 MODELING_ARCHITECTURE invariants — ADR references them.
4. Keep this table in sync with ADR frontmatter (enforced by `tests/architecture/test_adr_readme_matches_frontmatter.py`).

## Notes

- Aggregate DAMS schema version on `main`: see `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` (`version:` field). Catalogue path `0.1/` is the product label; it is not the LinkML semver. Living table: [SCHEMA-VERSION-TIMELINE.md](../migration/SCHEMA-VERSION-TIMELINE.md) (ADR-051).
- `superseded_by: MODELING_ARCHITECTURE.md` is reserved for drafts that are fully absorbed; Accepted ADRs use `superseded_by: []`.
- Post-audit P2 backlog (adapters, Distribution, vocabularies, ADR-053 follow-ups): [P2-BACKLOG.md](../migration/P2-BACKLOG.md) (ADR-055).
