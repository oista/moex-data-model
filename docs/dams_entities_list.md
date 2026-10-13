
# Сводный список сущностей DAMS (MOEX Data Model Specification)

## Группа 1. Ядро модели (DAMS Core) — три уровня

1. ModelPackage — версионируемый пакет модели (домена или решения)
2. ConceptualEntity — корпоративное понятие верхнего уровня
3. DomainContext — bounded context / доменная область
4. LogicalEntity — логическая сущность в рамках доменного контекста / решения
5. Attribute — атрибут логической сущности
6. Relationship — связь между логическими сущностями (роли, кардинальность)
7. TechnicalAsset (abstract) — квант данных; подклассы: DataCarrier, AccessPoint, DataContainer, ExecutionAsset
7a. DataCarrier — носитель данных (таблица, топик, файл, сообщение)
7b. AccessPoint — точка доступа (interface / operation / channel)
7c. DataContainer — контейнер (database, schema, broker, …)
7d. ExecutionAsset — исполняемый актив (pipeline, job)
7e. DataStructure / SchemaNode — структура и узлы схемы (вместо PhysicalField; ADR-038)
8. Mapping (+ RealizesMapping, EntityPhysicalMapping, FieldMapping, AlignsWithMapping) — типизированные коллекции (ADR-046)
9. GovernanceAssignment (abstract) — авторитетное назначение governance (ADR-049)
9a. ClassificationAssignment — присвоение классификации/чувствительности элементу
9b. OwnershipAssignment — присвоение data owner / steward / owning unit
10. ModelSelection / DataModelBinding — договорная проекция модели для контракта

## Группа 2. Аналитика и AI-слой

11. Metric — метрика (expression, grain, dimensions, owner)
12. PolicyBinding — привязка политики доступа/retention к элементу (subtype GovernanceAssignment)

## Группа 3. Интеграционный слой (новое из обсуждения потоков данных)

13. DataFlow — ссылочная проекция интеграции Clinkr (`integration_ref`; топология в TopologyView, ADR-048)
14. DataFlowEntityBinding — привязка логических сущностей/носителей к потоку (+ catalog_operation/participant refs)

## Группа 4. Справочники (Registries) — внешние ключи

15. ITSystem — ИТ-система (мастер: EAM)
16. ITSolution — ИТ-решение (может включать несколько систем)
17. ITPlatform — ИТ-платформа (мастер: EAM)
18. BusinessDomain — домен / предметная область (иерархический)
19. Role / OwnerRegistry — роли/подразделения-владельцы
20. GlossaryTerm — ссылка на термин корпоративного глоссария (внешний, EAM/Glossary)

## Группа 5. Дата-контракт (из MOEX-Data-Contracts-v2_2, зеркалируется/связывается, не дублируется)

21. DataContract — родительская спецификация контракта (DC-XXXXX)
22. IntegrationSpecification — дочерняя интеграционная спецификация (OpenAPI/AsyncAPI)
23. DataModelSpecification — дочерняя модельная спецификация (ссылка на ModelSelection)
24. DataQualitySpecification — дочерняя DQ-спецификация (SLA, пороги)
25. SpecificationImplementation — версия реализации конкретной спецификации во времени
26. Integration — карточка интеграции (Clinkr, источник контракта)

## Группа 6. Governance / жизненный цикл (сквозные mixins)

27. HasProvenance (mixin) — source, approval_status, approved_by/at
28. HasGovernanceClassification / HasBusinessClassification / HasPolicyBindings (mixins) — authored defaults; authoritative layer = GovernanceAssignment (ADR-049)
29. HasLifecycle / HasValidity (mixins) — статус (Draft/Active/Deprecated/Retired), valid_from/to
30. HasOwnership (mixin) — data_owner / steward / owning_unit (cascade ADR-023)
