---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR index (001â030)

**Status:** Proposed drafts  
**Date:** 2026-09-28  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2)

Ð¡Ð¿Ð¸ÑÐ¾Ðº ÑÐµÑÐµÐ½Ð¸Ð¹ Ð¸Ð· [linkml_architecture.md](../architecture/linkml_architecture.md) Â§ Â«ÐÐ»ÑÑÐµÐ²ÑÐµ ÑÐµÑÐµÐ½Ð¸ÑÂ». Ð­ÑÐ¾ **Ð¿ÑÐ¾ÐµÐºÑÑ ADR**, Ð½Ðµ Accepted: Ð¿ÑÐ¸ ÑÐ°ÑÑÐ¾Ð¶Ð´ÐµÐ½Ð¸Ð¸ Ð¿Ð¾Ð±ÐµÐ¶Ð´Ð°ÐµÑ Ð½Ð¾ÑÐ¼Ð°ÑÐ¸Ð²Ð½ÑÐ¹ Ð´Ð¾ÐºÑÐ¼ÐµÐ½Ñ ÑÐ´ÑÐ°.

Viewer-ÑÐµÑÐµÐ½Ð¸Ñ Ð¶Ð¸Ð²ÑÑ Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð¾: [viewer-decisions.md](../architecture/viewer-decisions.md). UI presentation â [ADR-015](ADR-015-viewer-ui-atlas.md) / [viewer-atlas](../design/viewer-atlas/README.md).

| ADR | Title | Scope today |
|---|---|---|
| [ADR-001](ADR-001-linkml-yaml-canonical.md) | LinkML YAML â ÐºÐ°Ð½Ð¾Ð½ Ð´Ð»Ñ DAMS / LinkML toolchain | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ Ð½Ð° ÑÐµÐºÑÑÐµÐ¼ ÑÑÐµÐ·Ðµ |
| [ADR-002](ADR-002-git-published-source.md) | Git â Ð¸ÑÑÐ¾ÑÐ½Ð¸Ðº Ð¾Ð¿ÑÐ±Ð»Ð¸ÐºÐ¾Ð²Ð°Ð½Ð½ÑÑ Ð²ÐµÑÑÐ¸Ð¹ | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ |
| [ADR-003](ADR-003-postgres-operational.md) | PostgreSQL â Ð¾Ð¿ÐµÑÐ°ÑÐ¸Ð¾Ð½Ð½Ð¾Ðµ ÑÑÐ°Ð½Ð¸Ð»Ð¸ÑÐµ Ð¸ Ð¿Ð¾Ð¸ÑÐºÐ¾Ð²Ð°Ñ Ð¿ÑÐ¾ÐµÐºÑÐ¸Ñ | Workbench, ÐµÑÑ Ð½ÐµÑ ÐºÐ¾Ð´Ð° |
| [ADR-004](ADR-004-modular-monolith.md) | ÐÐ¾Ð´ÑÐ»ÑÐ½ÑÐ¹ Ð¼Ð¾Ð½Ð¾Ð»Ð¸Ñ | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ (packages + apps/cli) |
| [ADR-005](ADR-005-drawdb-isolated.md) | drawDB â Ð¸Ð·Ð¾Ð»Ð¸ÑÐ¾Ð²Ð°Ð½Ð½Ð¾Ðµ self-hosted Ð¿ÑÐ¸Ð»Ð¾Ð¶ÐµÐ½Ð¸Ðµ | MVP: `apps/drawdb` + adapter + API/UI |
| [ADR-006](ADR-006-dbml-projection.md) | DBML â Ð¿ÑÐ¾ÐµÐºÑÐ¸Ñ, Ð½Ðµ source of truth | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ; Stage 5 round-trip MVP |
| [ADR-007](ADR-007-pydantic-dto-not-validator.md) | Pydantic â API DTO, Ð½Ðµ ÐµÐ´Ð¸Ð½ÑÑÐ²ÐµÐ½Ð½ÑÐ¹ validator | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ |
| [ADR-008](ADR-008-linkml-map-provider.md) | LinkML Map Ð·Ð° provider interface | Workbench / mappings, ÐµÑÑ Ð½ÐµÑ ÐºÐ¾Ð´Ð° |
| [ADR-009](ADR-009-schema-automator-draft-only.md) | schema-automator ÑÐ¾Ð»ÑÐºÐ¾ draft import | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ (ingest Ð½Ðµ Ð¸ÑÐ¿Ð¾Ð»ÑÐ·ÑÐµÑ) |
| [ADR-010](ADR-010-owl-not-primary-validation.md) | OWL Ð½Ðµ Ð¾ÑÐ½Ð¾Ð²Ð½Ð¾Ð¹ validation | Ð´ÐµÐ¹ÑÑÐ²ÑÐµÑ (ÐºÐ°ÑÐ°Ð»Ð¾Ð³ read-only) |
| [ADR-011](ADR-011-reproducible-artifacts.md) | Generated artifacts Ð²Ð¾ÑÐ¿ÑÐ¾Ð¸Ð·Ð²Ð¾Ð´Ð¸Ð¼Ñ | Stage 0: `requirements-linkml.txt` + `compare-golden` (contracts/JSON Schema); Ð¿Ð¾Ð»Ð½ÑÐ¹ matrix â ÑÑÐ°Ð¿ 6 |
| [ADR-012](ADR-012-semantic-diff-review.md) | ÐÑÐ±Ð»Ð¸ÐºÐ°ÑÐ¸Ñ ÑÐµÑÐµÐ· semantic diff Ð¸ review | Workbench; CLI + API preview + Web Review changes; PR attach â Ð½ÐµÑ |
| [ADR-013](ADR-013-specification-requirements-catalog.md) | ÐÐ°ÑÐ°Ð»Ð¾Ð³ ÑÑÐµÐ±Ð¾Ð²Ð°Ð½Ð¸Ð¹ Ðº ÑÐ¿ÐµÑÐ¸ÑÐ¸ÐºÐ°ÑÐ¸Ð¸ Ð² DAMS LinkML | DAMS explorer Â«Ð¢ÑÐµÐ±Ð¾Ð²Ð°Ð½Ð¸ÑÂ» |
| [ADR-014](ADR-014-fibo-profile-metamodel.md) | FIBO profile = Spec; content â  profile metamodel | metamodel YAML + Pydantic; refined by ADR-018 / ADR-024 |
| [ADR-015](ADR-015-viewer-ui-atlas.md) | MOEX Atlas â UI/UX ÑÑÐ°Ð½Ð´Ð°ÑÑ Publication Viewer | Proposed; visual redesign apps/viewer |
| [ADR-016](ADR-016-publication-section-kinds-and-profiles.md) | Publication section kinds and profiles | Proposed; DSP ProfileSpec; ontology row amended by ADR-024 |
| [ADR-017](ADR-017-external-specification-source-sync.md) | External specification source sync | Proposed; SpecificationSource + ROBOT/git adapters |
| [ADR-018](ADR-018-ontology-application-implementation.md) | OWL SpecImpl = application / extension ontology | Proposed; moex-fibo-application three-artifact body |
| [ADR-019](ADR-019-publication-contract-inheritance.md) | Publication contract inheritance | Proposed; satisfies / PublicationRequirement (DSP) |
| [ADR-020](ADR-020-external-specification-scope-and-term-selection.md) | External Specification Scope and Term Selection | Proposed; scope â  import; selection governance |
| [ADR-021](ADR-021-dams-implementation-profile-and-levels.md) | DAMS implementation profile + enterprise/solution levels | Proposed; dams-data-model only |
| [ADR-022](ADR-022-solution-xlsx-import.md) | Object/ObjectAttribute xlsx â DAMS solution import | Accepted; solution_xlsx + import-solution CLI |
| [ADR-023](ADR-023-governed-property-cascade.md) | Containment cascade of governed properties | Proposed; ownership / classification / policies |
| [ADR-024](ADR-024-unified-class-entity.md) | Unified Class entity; glossary as class view | Proposed; ontology ProfileSpec + edmc.fibo classes |
| [ADR-025](ADR-025-definition-cascade-and-glossary.md) | Definition cascade + glossary terminology | Proposed; HasDefinition / ScopedDefinition; semantic-axis resolver |
| [ADR-026](ADR-026-cmd-entity-metamodel.md) | Conceptual entity metamodel (tier, genesis, relation terms) | Proposed; RelationTerm / ExternalClassRef; model glossary view |
| [ADR-027](ADR-027-glossary-term-relations.md) | Glossary term relations (hierarchy vs associative vs equivalence) | Proposed; See also derived; no related-in-tree; SKOS = corporate projection |
| [ADR-028](ADR-028-package-documentation-section.md) | Package documentation section | Proposed; kind `documentation`; `docs/toc.yaml` + consumer-context + reserved `docs/adr/` |
| [ADR-029](ADR-029-cdm-from-er-sketch-and-realization.md) | ER sketch â CDM; no ConceptualAttribute; realization completeness (LDM-008) | Proposed; trading/party slice; warning only |
| [ADR-030](ADR-030-dams-uri-and-prefix-policy.md) | DAMS URI and prefix policy (Stage 8 Ontology) | Proposed; schema lint MOEX-ONT-*; ontology-profile |

## ÐÐ°Ðº Ð¿ÑÐ¸Ð½Ð¸Ð¼Ð°ÑÑ

1. Ð ÐµÐ²ÑÑ Ð¿Ð¾ [CHECKLIST.md](../architecture/CHECKLIST.md), ÐµÑÐ»Ð¸ Ð¿ÑÐ°Ð²ÐºÐ° Ð·Ð°ÑÑÐ°Ð³Ð¸Ð²Ð°ÐµÑ ÑÐ´ÑÐ¾.
2. Ð¡Ð¼ÐµÐ½Ð¸ÑÑ `status: Proposed` â `Accepted` ÑÐ¾Ð»ÑÐºÐ¾ Ð¿Ð¾ÑÐ»Ðµ ÑÐ²Ð½Ð¾Ð³Ð¾ ÑÐµÑÐµÐ½Ð¸Ñ.
3. ÐÐµ Ð´ÑÐ±Ð»Ð¸ÑÐ¾Ð²Ð°ÑÑ Ð¸Ð½Ð²Ð°ÑÐ¸Ð°Ð½ÑÑ Â§14 MODELING_ARCHITECTURE â ADR ÑÑÑÐ»Ð°ÐµÑÑÑ Ð½Ð° Ð½Ð¸Ñ.

| [ADR-034](ADR-034-lightweight-conceptual-property.md) | Îáëåã÷¸ííûé ConceptualProperty (âàðèàíò B) | Accepted; critical_data_element; deprecated slots |
| [ADR-035](ADR-035-value-domains.md) | ConceptualDomain / ValueDomain / SKOS | Accepted |
| [ADR-036](ADR-036-datatype-system.md) | DataType / NativeTypeBinding | Accepted |
| [ADR-037](ADR-037-attribute-semantics-migration.md) | Ìèãðàöèÿ ñåìàíòèêè LogicalAttribute | Accepted |
| [ADR-038](ADR-038-datastructure-and-schemanode.md) | DataStructure / SchemaNode (flat nodes) | Accepted; PhysicalField removed in 2.0.0 |
| [ADR-039](ADR-039-structure-node-addressing.md) | SchemaNode addressing (structure_id#local_key) | Accepted; amends ADR-030 |
| [ADR-040](ADR-040-message-integration-model.md) | Message integration model | Accepted; class in moex-structure |
| [ADR-041](ADR-041-schemanode-datatype-binding.md) | SchemaNode ? DataType / native_type | Accepted; does not duplicate ADR-036 |
| [ADR-042](ADR-042-integrity-digest-revisions.md) | integrity_digest and model revisions | Accepted; editorial renumber from colliding ADR-034 |
| [ADR-043](ADR-043-transitional-tags-registry.md) | Transitional element tags registry | Accepted; editorial renumber from colliding ADR-035 |
| [ADR-044](ADR-044-model-element-decomposition.md) | ModelElement decomposition (mixins, HasValidity, Mapping) | Proposed; inventory matrix; schema changes from 2.1.0 |
| [ADR-045](ADR-045-executable-constraint-matrix.md) | Executable constraint matrix (L1 rules / L2 validators / L3 SHACL) | Accepted; P0 invariants; INV-xxx; check-constraints in publish-gate |
