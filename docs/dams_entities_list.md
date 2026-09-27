
# Сводный список сущностей DAMS (MOEX Data Model Specification)

## Группа 1. Ядро модели (DAMS Core) — три уровня

1. ModelPackage — версионируемый пакет модели (домена или решения)
2. ConceptualEntity — корпоративное понятие верхнего уровня
3. DomainContext — bounded context / доменная область
4. LogicalEntity — логическая сущность в рамках доменного контекста / решения
5. Attribute — атрибут логической сущности
6. Relationship — связь между логическими сущностями (роли, кардинальность)
7. PhysicalObject — физический объект (таблица, топик, API endpoint, файл)
8. Mapping — маппинг между уровнями (лог <-> физ, домен <-> домен)
9. ClassificationAssignment — присвоение классификации/чувствительности элементу
10. ModelSelection / DataModelBinding — выбранная проекция модели для контракта

## Группа 2. Аналитика и AI-слой

11. Metric — метрика (expression, grain, dimensions, owner)
12. PolicyBinding — привязка политики доступа/retention к элементу

## Группа 3. Интеграционный слой (новое из обсуждения потоков данных)

13. DataFlow — поток данных между решениями/системами (топология)
14. DataFlowEntityBinding — привязка кросс-системной сущности к конкретному потоку

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

27. HasLineage (mixin) — source_system_ref, ingestion_timestamp
28. HasClassification (mixin) — класс данных, маркировка чувствительности
29. HasLifecycle (mixin) — статус (Draft/Active/Deprecated/Retired), даты
30. HasOwnership (mixin) — владелец/steward
