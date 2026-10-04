---
status: Draft
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# Ontology Catalog

**Норматив:** [MODELING_ARCHITECTURE.md](MODELING_ARCHITECTURE.md) (Proposed 0.2).  
При расхождении побеждает нормативный документ.

**Назначение:** read-only Ontology Catalog над референсными и локальными OWL-онтологиями. Модуль регистрирует версии релизов, индексирует сущности и связи и отдаёт единые read models для DAMS, глоссария и Publication Viewer. Это не редактор OWL и не triplestore.

## Роли в ядре платформы

| Роль | Экземпляр (этот этап) |
|---|---|
| `ModelingStandard` | OWL 2 |
| `ReferenceSpecification` | **FIBO ontology profile** (`moex-fibo-profile` — domains/modules/headers/annotation conventions); stubs Corporate Ontology, PROV-O |
| Upstream index (catalog) | **FIBO release** (`moex:ontology:fibo` — preview glossary / entity index); not a governed SpecImpl |
| `SpecificationImplementation` | **MOEX FIBO application ontology** (`moex-fibo-application` — imported module + extension + DAMS mapping); stubs MOEX HR / MOEX Data |
| External alignment (ADR-020) | **Scope** (`external-scopes/`) + **Term selection** (`external-selections/`) over pinned `external-sources/`; not an import of FIBO domains |

See [ADR-014](../adr/ADR-014-fibo-profile-metamodel.md): profile = Spec metamodel. See [ADR-018](../adr/ADR-018-ontology-application-implementation.md): governed OWL Impl = application / extension ontology; upstream release index ≠ SpecImpl. See [ADR-020](../adr/ADR-020-external-specification-scope-and-term-selection.md): scope ≠ import; selection ≠ full domain. ADR-010 still applies (OWL not primary YAML validation).

Новых `OWL*` классов в [modeling-kernel.yaml](modeling-kernel.yaml) нет. Typed OWL body живёт только в provider-пакете.

## Границы пакетов

```text
standard-owl
    OWL/RDF syntax, imports, axioms, parsing
             ↓
ontology-catalog
    референсные онтологии, сущности, связи, поиск
             ↓
semantic-mappings
    связи с DAMS и глоссарием (LinkML + SSSOM + SKOS)
             ↓
publication / viewer
    страницы, таблицы, дерево, карточка сущности
```

| Пакет | Вопрос | Текущий путь |
|---|---|---|
| `standard-owl` | как прочитать OWL | [packages/standard-owl](../../packages/standard-owl) |
| `ontology-catalog` | какие онтологии и сущности доступны | [packages/ontology-catalog](../../packages/ontology-catalog) |
| `semantic-mappings` | как связаны DAMS / glossary / ontology | [packages/semantic-mappings](../../packages/semantic-mappings) |
| `packages/ontology` | совместимый CLI `ontology.fibo` → CSV | тонкий shim над `standard-owl` |

`standard-owl` не знает про DAMS. `semantic-mappings` не знает про RDF-парсер. Viewer получает только read models / JSON-проекции и не интерпретирует RDF.

## Объектная модель каталога

Минимальные типы (Pydantic, frozen):

- `OntologyRelease` — id, ontology/version IRI, title, version, source, digest, imports, status (`registered` / `indexed` / `invalid` / `deprecated`)
- `OntologyEntity` — IRI, ontology_id, kind, label, definition, aliases, deprecated, replaced_by
- `OntologyRelation` — subject, predicate, object, asserted, source_ontology
- `SemanticBinding` — subject/object refs, predicate, justification, confidence, author, status, mapping_set_id

`OntologyEntity` — read model над OWL-ресурсом, не полная сериализация аксиом. Аксиомы остаются внутри OWL provider.

## Стек первого этапа

| Компонент | Роль |
|---|---|
| OAK (oaklib) | основной `OntologyProvider`: lookup, labels, hierarchy, subgraphs |
| RDFLib | offline parser и fallback для локальных RDF/XML / Turtle |
| LinkML mappings | `class_uri`, `slot_uri`, `meaning`, `exact_mappings` / `close_mappings` / … |
| SSSOM | managed mapping sets с provenance |
| SKOS | бизнес-глоссарий как `Concept` / `ConceptScheme` (отдельно от `owl:Class`) |
| SQLite | перестраиваемая search projection |

Вне этапа: reasoner, SPARQL endpoint, Neo4j, OLS4, PostgreSQL, редактор OWL, `linkml-owl` как фундамент браузера.

## Хранение

```text
Git descriptors + source release
         ↓
OAK / RDFLib ingestion
         ↓
SQLite search projection
         ↓
Ontology read models
         ↓
Publication Viewer / API
```

Канон — Git descriptor и зафиксированный upstream release. Индекс полностью перестраиваемый. RDF upstream в Git не коммитится.

Дескрипторы: `model-assets/implementations/ontologies/`.

## Связи с DAMS и глоссарием

| Ситуация | Механизм |
|---|---|
| Ontology entity — первичная семантика LinkML-класса | `class_uri` |
| Ontology property — семантика слота | `slot_uri` |
| Enum value обозначает concept | `meaning` |
| Простое соответствие | LinkML `exact_mappings` / `close_mappings` / … |
| Управляемое соответствие с автором и статусом | `SemanticBinding` (SSSOM) |
| Связи между терминами **корпоративного** глоссария (hierarchy + related) | SKOS concept-scheme **проекция** (`broader` / `narrower` / `related`); не слоты на `GlossaryTerm` ([ADR-027](../adr/ADR-027-glossary-term-relations.md)) |
| Иерархия / See also в **онтологическом** глоссарии | Hierarchy = `rdfs:subClassOf`; associative = object properties → UX See also (ADR-024 / ADR-027); не SKOS-дерево |
| Иерархия / See also в **model** glossary | Hierarchy = `parent_concept_ref`; associative = `Relationship` / `RelationTerm` (ADR-026 / ADR-027) |
| Эталонное определение ConceptualEntity / LogicalEntity | `description` (`skos:definition`) + ADR-025 cascade; наследование из онтологии только при exactMatch / equivalentClass |
| Привязка к корпоративному глоссарию | `glossary_term_refs` (term assignment; не источник определения; не associative related — ADR-027) |
| Источник унаследованного / adapted определения | `definition_source_ref` (ADR-025); не See also (ADR-027) |

DAMS-класс `Mapping` в `moex-core.yaml` остаётся соответствием conceptual / logical / physical внутри модели решения; он не заменяет SSSOM.

`GlossaryTerm` в registries остаётся `RegistryEntry` — проекция записи корпоративного глоссария. SKOS concept scheme — отдельная **проекция**, не источник истины; термин не становится `owl:Class` автоматически. «Глоссарий» в publication viewer — всегда **view** определений заданного охвата (ADR-024 / ADR-025), не отдельная сущность. Три семейства связей (hierarchy / associative / equivalence) — [ADR-027](../adr/ADR-027-glossary-term-relations.md); related не кладётся в дерево.

## Publication Viewer

UI потребляет только:

- `OntologySummary`
- `OntologyEntityCard`
- `OntologyTreeNode`
- `SemanticBindingView`

Пять представлений: каталог релизов, поиск сущностей, иерархия (asserted predicate), карточка, backlinks. Сборка пишет JSON, совместимый с существующими секциями viewer (`glossary`, `tree`, `entity-table`). Новый runtime backend не требуется.

## Первый инкремент

1. FIBO exporter → адаптер внутри `standard-owl`.
2. `OntologyRelease` / `OntologyEntity` / `OntologyRelation` + SQLite index.
3. OAK (+ RDFLib fallback) для lookup и asserted hierarchy.
4. FIBO как первая indexed reference ontology; остальные — `registered` stubs.
5. Один SSSOM set `dams-fibo` и LinkML mapping extractor на фикстуре.
6. SKOS concept scheme (маленький) без расширения DAMS schema.
7. Preview JSON + `publish.yaml` во viewer.

## Связанные документы

- [MODELING_ARCHITECTURE.md](MODELING_ARCHITECTURE.md) — норматив
- [ADR-014](../adr/ADR-014-fibo-profile-metamodel.md) — FIBO profile vs release content
- [app_model.md](app_model.md) — целевая раскладка пакетов
- [viewer-decisions.md](viewer-decisions.md) — статический viewer, без RDF в UI
- [linkml_architecture.md](linkml_architecture.md) — Workbench / Ontology Engine (gen-owl ≠ catalog)
