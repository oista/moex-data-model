---
status: Draft
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# MOEX Data Model: раскладка пакетов и object model (черновик)

**Норматив:** [MODELING_ARCHITECTURE.md](MODELING_ARCHITECTURE.md) (Proposed 0.2).  
При расхождении побеждает нормативный документ.  
**Статус этого файла:** черновик целевой раскладки пакетов и provider object model (`target-after-slice`).  
**Уже совпало с репо:** `model-assets/`, `generated/`, `apps/cli/`, `apps/viewer/`, пакеты slice (`modeling-kernel`, `standard-linkml`, `specification-dams`, `publication`), `standard-owl`, `ontology-catalog`.  
**Уже совпало (roadmap 1–4):** `generated/contracts` (moex_dams_contracts), `OWLStandardProvider`, `packages/git-adapter`, CLI `lint|compile|diagram|diff|validate|publish|import|map|semantic-diff`, `apps/api` operational slice.  
**Уже совпало (Stage 3 narrow-v2):** identity/members/jobs/artifacts/model_index tables + ports; workspace/job/index API + Idempotency-Key; GitHub read-only `GitProvider`.  
**Уже совпало (Web Workbench MVP):** `apps/web` React/Vite shell — dashboard, workspaces, MDM model page, validation job report.  
**Уже совпало (Workbench editors):** Monaco YAML + `workspace_document` draft API + validate `source=draft`.  
**Уже совпало (Entity form slice):** controlled mutations add/update/delete LogicalEntity/LogicalAttribute; dirty Monaco → PUT before mutation.  
**Уже совпало (Stage 3 narrow-v3):** `publication_request` + publish API + GitHub write / local branch+stub review into this repo.  
**Already shipped (Semantic diff preview):** kernel `SemanticDiffReport`; `moex-model semantic-diff`; `POST /workspaces/{id}/semantic-diff`; Web **Review changes**.  
**Already shipped (Stage 4/5 close-out):** relationship/mapping forms, Model explorer, artifacts panel, `packages/drawdb-adapter`, `apps/drawdb`, Alembic `diagram_layout` (`0006`), Workbench diagram page.  
**Already shipped (Stage 6 golden matrix):** OWL/SHACL/`moex-dams.dbml`/Mermaid in `compare-golden` (+ contracts/JSON Schema).

**Already shipped (Stage 1 residual):** `SchemaRepository` + `DamsAssetRepository`; `diagnostic_to_wire` in CLI/API validation diagnostics; `build_element_index` shared with API model-index; `DamsModelGraphView` includes `relationships`.

**Still-later:** live field-level Monaco↔form binding, merge automation / PR attach, `apps/worker`, OIDC, domain authz/RLS, `external_registry_cache`, async workers; Stage 1 leftovers (repository-root graph, SchemaLoader types); auto-promote import draft→ModelPackage; live EAM/Clinkr adapters.
`packages/ontology/` остаётся shim. Миграция путей: [docs/migration/model-src-to-model-assets.md](../migration/model-src-to-model-assets.md).

## Предметная модель: роли как экземпляры, не subclass

```text
ModelUniverse
├── ModelingStandard (instances)
│   ├── linkml@1.x
│   ├── openapi@3.1
│   ├── owl@2
│   ├── json-schema@2020-12      # как standard family; generated artifacts ≠ implementation
│   └── shacl@1.2
│
├── ReferenceSpecification (instances)
│   ├── moex-dams@0.1            # expressed_in: linkml; root_type: MOEXModelRepository
│   ├── moex-api-profile@1.0
│   ├── moex-ontology-profile@1.0
│   ├── data-contract profile…
│   └── quality profile…
│
├── SpecificationImplementation (envelopes; typed body in provider)
│   ├── mdm-solution@0.1         # conforms_to: moex-dams@0.1; kind: linkml
│   ├── order-service openapi…
│   └── domain ontology…
│
└── StandardMapping (instances)
    ├── projection / import / export / migration mappings
```

Запрещено моделировать роли наследованием в kernel:

```text
# НЕ ДЕЛАТЬ
LinkMLStandard is_a ModelingStandard
DamsSpecification is_a ReferenceSpecification
DamsModelImplementation is_a LinkMLImplementation
```

DAMS — instance `ReferenceSpecification` с `specification_kind: data_model` и `expressed_in → linkml`.  
Типы solution-модели — generated contracts из `moex-dams.yaml`, не рукописный второй metamodel.

## Связи

```text
ModelingStandard
    └── expressed_in ← ReferenceSpecification
            └── conforms_to ← SpecificationImplementation
                    └── contains → provider-owned ImplementedElement identities

SpecificationImplementation
    └── implements → external ITSolution / system (optional)
    └── transformed through StandardMapping
            └── produces SpecificationImplementation | GeneratedArtifact
```

## Иерархия runtime-моделей (kernel + providers)

```text
# Kernel package (moex_modeling) — только envelopes / coordinates
ModelingStandard
ReferenceSpecification
SpecificationImplementation   # concrete envelope; body_ref opaque
StandardMapping
ConformanceAssessment
ConformanceReport
Diagnostic
ModelUniverse

# Provider packages — typed bodies (NOT in modeling-kernel.yaml)
LinkMLImplementationBody          # packages/standard-linkml
  ├── LinkMLSchemaElement
  ├── LinkMLClassElement
  ├── LinkMLSlotElement
  ├── LinkMLTypeElement
  ├── LinkMLEnumElement
  └── LinkMLInstanceElement

OpenAPIImplementationBody         # packages/standard-openapi (later)
OWLImplementationBody             # packages/standard-owl
```

Ontology Catalog (read models, не kernel): `OntologyRelease`, `OntologyEntity`, `OntologyRelation`, `SemanticBinding` — см. [ontology-catalog.md](ontology-catalog.md).  
Совместимый CLI экспорта FIBO CSV пока живёт в `packages/ontology` как shim над `standard-owl`.

Нет корневого класса `MetaModel`, объединяющего всё через наследование.

## Целевая структура проекта (target-after-slice)

Ниже — целевое дерево. Узлы без пометки «позднее» / «still-later» уже присутствуют в репозитории (иногда с меньшей детализацией файлов, чем в дереве).

```text
moex-data-model/
├── README.md
├── pyproject.toml
├── uv.lock
├── Makefile
│
├── apps/
│   ├── cli/
│   │   └── src/moex_model_cli/
│   │       ├── commands/
│   │       │   ├── standard.py
│   │       │   ├── specification.py
│   │       │   ├── implementation.py
│   │       │   ├── validate.py
│   │       │   ├── transform.py
│   │       │   └── publish.py
│   │       ├── presenters/
│   │       ├── bootstrap.py
│   │       └── __main__.py
│   │
│   ├── viewer/                      # есть: apps/viewer
│   │   └── src/moex_model_viewer/
│   │       ├── routes/
│   │       ├── templates/
│   │       ├── static/
│   │       ├── presenters/
│   │       └── bootstrap.py
│   │
│   ├── api/                         # будущий HTTP adapter
│   │   └── src/moex_model_api/
│   │       ├── routers/
│   │       ├── schemas/
│   │       ├── dependencies.py
│   │       └── bootstrap.py
│   │
│   └── worker/                      # будущие фоновые задания
│       └── src/moex_model_worker/
│           ├── tasks/
│           └── bootstrap.py
│
├── packages/
│   ├── modeling-kernel/
│   │   └── src/moex_modeling/
│   │       ├── shared/
│   │       │   ├── identifiers.py
│   │       │   ├── versions.py
│   │       │   ├── digests.py
│   │       │   ├── lifecycle.py
│   │       │   ├── provenance.py
│   │       │   └── diagnostics.py
│   │       │
│   │       ├── standards/
│   │       │   ├── domain/
│   │       │   │   ├── standard.py
│   │       │   │   ├── capabilities.py
│   │       │   │   ├── dialect.py
│   │       │   │   └── processor.py
│   │       │   ├── application/
│   │       │   │   ├── commands.py
│   │       │   │   ├── queries.py
│   │       │   │   ├── services.py
│   │       │   │   └── ports.py
│   │       │   └── public.py
│   │       │
│   │       ├── specifications/
│   │       │   ├── domain/
│   │       │   │   ├── specification.py
│   │       │   │   ├── conformance_policy.py
│   │       │   │   ├── imports.py
│   │       │   │   └── profile.py
│   │       │   ├── application/
│   │       │   │   ├── commands.py
│   │       │   │   ├── queries.py
│   │       │   │   ├── services.py
│   │       │   │   └── ports.py
│   │       │   └── public.py
│   │       │
│   │       ├── implementations/
│   │       │   ├── domain/
│   │       │   │   ├── implementation.py
│   │       │   │   ├── envelopes.py
│   │       │   │   ├── revisions.py
│   │       │   │   └── lifecycle.py
│   │       │   ├── application/
│   │       │   │   ├── commands.py
│   │       │   │   ├── queries.py
│   │       │   │   ├── services.py
│   │       │   │   └── ports.py
│   │       │   └── public.py
│   │       │
│   │       ├── conformance/
│   │       │   ├── domain/
│   │       │   │   ├── assessment.py
│   │       │   │   ├── report.py
│   │       │   │   └── rule.py
│   │       │   ├── application/
│   │       │   │   └── assess_conformance.py
│   │       │   └── public.py
│   │       │
│   │       ├── transformations/
│   │       │   ├── domain/
│   │       │   │   ├── mapping.py
│   │       │   │   ├── semantic_loss.py
│   │       │   │   ├── projection.py
│   │       │   │   └── provenance.py
│   │       │   ├── application/
│   │       │   │   ├── transform.py
│   │       │   │   └── ports.py
│   │       │   └── public.py
│   │       │
│   │       ├── universe/
│   │       │   ├── domain/
│   │       │   │   ├── universe.py
│   │       │   │   ├── relations.py
│   │       │   │   ├── graph_view.py
│   │       │   │   └── indexes.py
│   │       │   ├── application/
│   │       │   │   ├── build_universe.py
│   │       │   │   └── query_universe.py
│   │       │   └── public.py
│   │       │
│   │       └── public.py
│   │
│   ├── standard-linkml/             # первый модуль: ingest ER-словаря → ModelPackage
│   │   └── src/moex_standard_linkml/
│   │       ├── ingest/              # XLS/CSV dictionary → DAMS ModelPackage + envelope
│   │       ├── domain/              # target-after-slice
│   │       │   ├── body.py
│   │       │   ├── elements.py
│   │       │   └── references.py
│   │       ├── adapters/
│   │       │   ├── parser.py
│   │       │   ├── schema_view.py
│   │       │   ├── validator.py
│   │       │   ├── serializer.py
│   │       │   └── generator.py
│   │       ├── mappings/
│   │       │   ├── contract_to_body.py
│   │       │   └── body_to_graph.py
│   │       ├── contracts/
│   │       │   └── generated/
│   │       ├── provider.py
│   │       └── public.py
│   │
│   ├── standard-openapi/            # позднее
│   ├── standard-owl/                # OWL provider (parse / OAK); см. ontology-catalog.md
│   ├── ontology-catalog/            # Ontology Catalog: releases, entities, search index
│   ├── semantic-mappings/           # LinkML mappings + SSSOM + SKOS projections
│   │
│   ├── specification-dams/
│   │   └── src/moex_dams/
│   │       ├── domain/              # thin facades over generated contracts only
│   │       ├── rules/               # structural, references, governance, mappings, compatibility
│   │       │   ├── structural.py
│   │       │   ├── references.py
│   │       │   ├── governance.py
│   │       │   ├── mappings.py
│   │       │   └── compatibility.py
│   │       ├── mappings/
│   │       │   ├── linkml_to_dams.py
│   │       │   └── dams_to_graph.py
│   │       └── public.py
│   │       # НЕ дублировать ConceptualEntity/LogicalEntity вручную —
│   │       # типы из generated/contracts/moex-dams (из moex-dams.yaml)
│   │
│   ├── publication/
│   │   └── src/moex_publication/
│   │       ├── domain/
│   │       │   ├── manifest.py
│   │       │   └── read_models.py
│   │       ├── application/
│   │       │   ├── build_publication.py
│   │       │   └── ports.py
│   │       ├── adapters/
│   │       │   ├── normalizers/
│   │       │   ├── renderers/
│   │       │   └── search_index.py
│   │       └── public.py
│   │
│   ├── git-adapter/
│   │   └── src/moex_git/
│   │
│   └── artifact-adapters/
│       └── src/moex_artifacts/
│           ├── filesystem.py
│           ├── object_storage.py
│           └── manifests.py
│
├── model-assets/
│   ├── standards/
│   │   ├── linkml/1.x/standard.yaml
│   │   ├── openapi/3.1/standard.yaml
│   │   ├── owl/2/standard.yaml
│   │   ├── json-schema/2020-12/standard.yaml
│   │   └── shacl/1.2/standard.yaml
│   │
│   ├── specifications/
│   │   ├── moex-dams/0.1/
│   │   │   ├── specification.yaml
│   │   │   ├── schemas/             # есть: model-assets/.../schemas/
│   │   │   │   ├── moex-types.yaml
│   │   │   │   ├── moex-registries.yaml
│   │   │   │   ├── moex-governance.yaml
│   │   │   │   ├── moex-core.yaml
│   │   │   │   ├── moex-integration.yaml
│   │   │   │   ├── moex-contract-binding.yaml
│   │   │   │   ├── moex-analytics.yaml
│   │   │   │   └── moex-dams.yaml    # tree_root: MOEXModelRepository
│   │   │   ├── policies/
│   │   │   ├── examples/
│   │   │   └── conformance/
│   │   ├── moex-api-profile/1.0/
│   │   └── moex-ontology-profile/1.0/
│   │
│   ├── implementations/
│   │   ├── solutions/mdm/
│   │   ├── services/order-api/
│   │   └── ontologies/fibo-party/
│   │
│   └── transformations/
│
├── generated/
│   ├── contracts/
│   ├── artifacts/
│   └── manifests/
│
├── tests/
│   ├── architecture/
│   │   ├── test_dependency_rules.py
│   │   └── test_public_apis.py      # incl. distinct TSpecBody/TImplBody
│   ├── kernel/
│   ├── standards/
│   ├── specifications/
│   ├── conformance/
│   ├── integration/
│   ├── golden/
│   └── e2e/
│
├── docs/
│   ├── architecture/
│   │   ├── MODELING_ARCHITECTURE.md   # normative
│   │   ├── modeling-kernel.yaml
│   │   ├── app_model.md               # this file
│   │   ├── linkml_architecture.md     # Workbench / LinkML toolchain
│   │   ├── CHECKLIST.md
│   │   └── diagrams/
│   ├── adr/
│   ├── standards/
│   ├── specifications/
│   ├── development/
│   └── migration/
│
├── tools/
│   └── architecture-check/
│
├── config/
│   ├── validation/
│   ├── generation/
│   ├── publication/
│   └── logging/
│
└── .github/
    └── workflows/
        ├── check.yaml
        ├── conformance.yaml
        ├── generate.yaml
        └── publish.yaml
```

## Заметки по границам

- `specification-dams` владеет **rules + mappings + graph views**, не второй копией LinkML-классов DAMS.
- `standard-linkml` владеет typed body / elements / SchemaView adapter; первый реализованный модуль — `ingest/` (ER-словарь XLS/CSV → DAMS `ModelPackage` + envelope).
- `publication` — read model; не source of truth.
- Добавление OpenAPI/OWL не меняет classes в `modeling-kernel.yaml` (`make architecture-check`).
