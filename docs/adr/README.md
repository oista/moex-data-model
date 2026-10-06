---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR index (001–030)

**Status:** Proposed drafts  
**Date:** 2026-09-28  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2)

Спиѝок решений из [linkml_architecture.md](../architecture/linkml_architecture.md) § «Ключевые решениѝ». Это **проекты ADR**, не Accepted: при раѝхождении побеждает нормативный документ ѝдра.

Viewer-решениѝ живут отдельно: [viewer-decisions.md](../architecture/viewer-decisions.md). UI presentation — [ADR-015](ADR-015-viewer-ui-atlas.md) / [viewer-atlas](../design/viewer-atlas/README.md).

| ADR | Title | Scope today |
|---|---|---|
| [ADR-001](ADR-001-linkml-yaml-canonical.md) | LinkML YAML — канон длѝ DAMS / LinkML toolchain | дейѝтвует на текущем ѝрезе |
| [ADR-002](ADR-002-git-published-source.md) | Git — иѝточник опубликованных верѝий | дейѝтвует |
| [ADR-003](ADR-003-postgres-operational.md) | PostgreSQL — операционное хранилище и поиѝковаѝ проекциѝ | Workbench, ещё нет кода |
| [ADR-004](ADR-004-modular-monolith.md) | Модульный монолит | дейѝтвует (packages + apps/cli) |
| [ADR-005](ADR-005-drawdb-isolated.md) | drawDB — изолированное self-hosted приложение | MVP: `apps/drawdb` + adapter + API/UI |
| [ADR-006](ADR-006-dbml-projection.md) | DBML — проекциѝ, не source of truth | дейѝтвует; Stage 5 round-trip MVP |
| [ADR-007](ADR-007-pydantic-dto-not-validator.md) | Pydantic — API DTO, не единѝтвенный validator | дейѝтвует |
| [ADR-008](ADR-008-linkml-map-provider.md) | LinkML Map за provider interface | Workbench / mappings, ещё нет кода |
| [ADR-009](ADR-009-schema-automator-draft-only.md) | schema-automator только draft import | дейѝтвует (ingest не иѝпользует) |
| [ADR-010](ADR-010-owl-not-primary-validation.md) | OWL не оѝновной validation | дейѝтвует (каталог read-only) |
| [ADR-011](ADR-011-reproducible-artifacts.md) | Generated artifacts воѝпроизводимы | Stage 0: `requirements-linkml.txt` + `compare-golden` (contracts/JSON Schema); полный matrix — ѝтап 6 |
| [ADR-012](ADR-012-semantic-diff-review.md) | Публикациѝ через semantic diff и review | Workbench; CLI + API preview + Web Review changes; PR attach — нет |
| [ADR-013](ADR-013-specification-requirements-catalog.md) | Каталог требований к ѝпецификации в DAMS LinkML | DAMS explorer «Требованиѝ» |
| [ADR-014](ADR-014-fibo-profile-metamodel.md) | FIBO profile = Spec; content ≠ profile metamodel | metamodel YAML + Pydantic; refined by ADR-018 / ADR-024 |
| [ADR-015](ADR-015-viewer-ui-atlas.md) | MOEX Atlas — UI/UX ѝтандарт Publication Viewer | Proposed; visual redesign apps/viewer |
| [ADR-016](ADR-016-publication-section-kinds-and-profiles.md) | Publication section kinds and profiles | Proposed; DSP ProfileSpec; ontology row amended by ADR-024 |
| [ADR-017](ADR-017-external-specification-source-sync.md) | External specification source sync | Proposed; SpecificationSource + ROBOT/git adapters |
| [ADR-018](ADR-018-ontology-application-implementation.md) | OWL SpecImpl = application / extension ontology | Proposed; moex-fibo-application three-artifact body |
| [ADR-019](ADR-019-publication-contract-inheritance.md) | Publication contract inheritance | Proposed; satisfies / PublicationRequirement (DSP) |
| [ADR-020](ADR-020-external-specification-scope-and-term-selection.md) | External Specification Scope and Term Selection | Proposed; scope ≠ import; selection governance |
| [ADR-021](ADR-021-dams-implementation-profile-and-levels.md) | DAMS implementation profile + enterprise/solution levels | Proposed; dams-data-model only |
| [ADR-022](ADR-022-solution-xlsx-import.md) | Object/ObjectAttribute xlsx → DAMS solution import | Accepted; solution_xlsx + import-solution CLI |
| [ADR-023](ADR-023-governed-property-cascade.md) | Containment cascade of governed properties | Proposed; ownership / classification / policies |
| [ADR-024](ADR-024-unified-class-entity.md) | Unified Class entity; glossary as class view | Proposed; ontology ProfileSpec + edmc.fibo classes |
| [ADR-025](ADR-025-definition-cascade-and-glossary.md) | Definition cascade + glossary terminology | Proposed; HasDefinition / ScopedDefinition; semantic-axis resolver |
| [ADR-026](ADR-026-cmd-entity-metamodel.md) | Conceptual entity metamodel (tier, genesis, relation terms) | Proposed; RelationTerm / ExternalClassRef; model glossary view |
| [ADR-027](ADR-027-glossary-term-relations.md) | Glossary term relations (hierarchy vs associative vs equivalence) | Proposed; See also derived; no related-in-tree; SKOS = corporate projection |
| [ADR-028](ADR-028-package-documentation-section.md) | Package documentation section | Proposed; kind `documentation`; `docs/toc.yaml` + consumer-context + reserved `docs/adr/` |
| [ADR-029](ADR-029-cdm-from-er-sketch-and-realization.md) | ER sketch → CDM; no ConceptualAttribute; realization completeness (LDM-008) | Proposed; trading/party slice; warning only |
| [ADR-030](ADR-030-dams-uri-and-prefix-policy.md) | DAMS URI and prefix policy (Stage 8 Ontology) | Proposed; schema lint MOEX-ONT-*; ontology-profile |

## Как принимать

1. Ревью по [CHECKLIST.md](../architecture/CHECKLIST.md), еѝли правка затрагивает ѝдро.
2. Сменить `status: Proposed` → `Accepted` только поѝле ѝвного решениѝ.
3. Не дублировать инварианты §14 MODELING_ARCHITECTURE — ADR ѝѝылаетѝѝ на них.

| [ADR-034](ADR-034-lightweight-conceptual-property.md) | ����������� ConceptualProperty (������� B) | Accepted; critical_data_element; deprecated slots |
| [ADR-035](ADR-035-value-domains.md) | ConceptualDomain / ValueDomain / SKOS | Accepted |
| [ADR-036](ADR-036-datatype-system.md) | DataType / NativeTypeBinding | Accepted |
| [ADR-037](ADR-037-attribute-semantics-migration.md) | �������� ��������� LogicalAttribute | Accepted |
| [ADR-038](ADR-038-datastructure-and-schemanode.md) | DataStructure / SchemaNode (flat nodes) | Accepted; PhysicalField removed in 2.0.0 |
| [ADR-039](ADR-039-structure-node-addressing.md) | SchemaNode addressing (structure_id#local_key) | Accepted; amends ADR-030 |
| [ADR-040](ADR-040-message-integration-model.md) | Message integration model | Accepted; class in moex-structure |
| [ADR-041](ADR-041-schemanode-datatype-binding.md) | SchemaNode ? DataType / native_type | Accepted; does not duplicate ADR-036 |
| [ADR-042](ADR-042-integrity-digest-revisions.md) | integrity_digest and model revisions | Accepted; editorial renumber from colliding ADR-034 |
| [ADR-043](ADR-043-transitional-tags-registry.md) | Transitional element tags registry | Accepted; editorial renumber from colliding ADR-035 |
| [ADR-044](ADR-044-model-element-decomposition.md) | ModelElement decomposition (mixins, HasValidity, Mapping) | Proposed; inventory matrix; schema changes from 2.1.0 |
| [ADR-045](ADR-045-executable-constraint-matrix.md) | Executable constraint matrix (L1 rules / L2 validators / L3 SHACL) | Proposed; P0 invariants; INV-xxx; check-constraints |
