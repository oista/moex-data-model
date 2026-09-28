# moex_dams



URI: https://data.moex.com/dams/v0.1

Name: moex_dams



## Classes

| Class | Description |
| --- | --- |
| [BusinessDomain](BusinessDomain.md) | Бизнес-домен или предметная область; мастер определяется архитектурным govern... |
| [BusinessProcess](BusinessProcess.md) | Ссылка на бизнес-процесс или его шаг в BPMN-репозитории |
| [ClassificationAssignment](ClassificationAssignment.md) | Версионируемое назначение категории классификации элементу модели с основание... |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |
| [DataClassificationTerm](DataClassificationTerm.md) | Специальная категория чувствительности или регулирования, например ПДн или ин... |
| [DataContractReference](DataContractReference.md) | Ссылка на дата-контракт в корпоративном дата-каталоге |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |
| [Dimension](Dimension.md) | Переиспользуемое аналитическое измерение, связанное с логическими атрибутами |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |
| [FormalCheck](FormalCheck.md) | Одна машиночитаемая проверка требования |
| [GlossaryTerm](GlossaryTerm.md) | Термин корпоративного бизнес-глоссария |
| [HasBusinessClassification](HasBusinessClassification.md) | Классификация роли и бизнес-значимости логической сущности |
| [HasGovernanceClassification](HasGovernanceClassification.md) | Базовая и специальная классификация чувствительности данных |
| [HasLifecycle](HasLifecycle.md) | Mixin жизненного цикла: статус, период действия и ссылка на заменяющий элемен... |
| [HasOwnership](HasOwnership.md) | Mixin владения: data owner, data steward и организационное подразделение |
| [HasPolicyBindings](HasPolicyBindings.md) | Mixin привязки управляемых политик к элементу модели |
| [HasProvenance](HasProvenance.md) | Mixin происхождения и согласования: исходный артефакт, evidence, статус и сог... |
| [IntegrationReference](IntegrationReference.md) | Ссылка на интеграцию в Clinkr |
| [ITPlatform](ITPlatform.md) | ИТ-платформа; мастер данных — EAM |
| [ITSolution](ITSolution.md) | ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM |
| [ITSystem](ITSystem.md) | ИТ-система; мастер данных — EAM |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |
| [Mapping](Mapping.md) | Явное соответствие между элементами концептуального, логического и физическог... |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |
| [ModelElement](ModelElement.md) | Абстрактный корень иерархии элементов модели: общая идентичность (element_id)... |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |
| [ModelSelection](ModelSelection.md) | Переиспользуемый набор выбранных сущностей, атрибутов и физических представле... |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |
| [OrganizationUnit](OrganizationUnit.md) | Организационное подразделение |
| [PhysicalField](PhysicalField.md) | Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |
| [Policy](Policy.md) | Политика доступа, хранения, качества или архитектурный инвариант |
| [PolicyBinding](PolicyBinding.md) | Применение управляемой политики к элементу модели |
| [RegistryEntry](RegistryEntry.md) | Локальная ссылочная проекция записи внешней мастер-системы; не является масте... |
| [Relationship](Relationship.md) | Именованная связь между логическими или концептуальными сущностями |
| [RequirementCatalog](RequirementCatalog.md) | Контейнер инстансов SpecificationRequirement вне ModelPackage |
| [Role](Role.md) | Управляемая роль владельца, стюарда, потребителя или согласующего |
| [SelectedAttribute](SelectedAttribute.md) | Выбранный атрибут и соответствующее физическое поле payload, таблицы или сооб... |
| [SelectedEntity](SelectedEntity.md) | Выбранная для интеграции логическая сущность |
| [SpecificationRequirement](SpecificationRequirement.md) | Нормативное требование к модели, соответствующей reference specification (кат... |



## Slots

| Slot | Description |
| --- | --- |
| [aggregation_function](aggregation_function.md) |  |
| [aliases](aliases.md) |  |
| [api_version](api_version.md) |  |
| [approval_status](approval_status.md) |  |
| [approved_at](approved_at.md) |  |
| [approved_by_ref](approved_by_ref.md) |  |
| [assignment_id](assignment_id.md) |  |
| [associative](associative.md) |  |
| [attributes](attributes.md) |  |
| [business_importance](business_importance.md) |  |
| [business_process_refs](business_process_refs.md) |  |
| [catalog_id](catalog_id.md) |  |
| [check_id](check_id.md) |  |
| [classification_assignments](classification_assignments.md) |  |
| [classification_rationale](classification_rationale.md) |  |
| [classification_source](classification_source.md) |  |
| [classification_term_ref](classification_term_ref.md) |  |
| [classified_element_ref](classified_element_ref.md) |  |
| [code](code.md) |  |
| [compatibility_baseline_ref](compatibility_baseline_ref.md) |  |
| [compatibility_mode](compatibility_mode.md) |  |
| [conceptual_entities](conceptual_entities.md) |  |
| [conceptual_entity_refs](conceptual_entity_refs.md) |  |
| [confidence](confidence.md) |  |
| [context_ref](context_ref.md) |  |
| [contract_ref](contract_ref.md) |  |
| [data_class](data_class.md) |  |
| [data_flows](data_flows.md) |  |
| [data_model_bindings](data_model_bindings.md) |  |
| [data_owner_ref](data_owner_ref.md) |  |
| [data_steward_ref](data_steward_ref.md) |  |
| [default_value](default_value.md) |  |
| [deprecated_by_ref](deprecated_by_ref.md) |  |
| [derived_expression](derived_expression.md) |  |
| [description](description.md) |  |
| [diagnostic_code](diagnostic_code.md) | Мост к DAMS-STRUCT-* / DAMS-REF-* / будущим DAMS-REQ-* |
| [dimension_attribute_refs](dimension_attribute_refs.md) |  |
| [dimensions](dimensions.md) |  |
| [direction](direction.md) |  |
| [domain_contexts](domain_contexts.md) |  |
| [domain_ref](domain_ref.md) |  |
| [domain_refs](domain_refs.md) |  |
| [element_id](element_id.md) |  |
| [entity_bindings](entity_bindings.md) |  |
| [entity_type](entity_type.md) |  |
| [evidence_refs](evidence_refs.md) |  |
| [expression](expression.md) | Свободная LinkML-ish заметка при kind=custom |
| [filter_expression](filter_expression.md) |  |
| [flow_ref](flow_ref.md) |  |
| [formal_checks](formal_checks.md) |  |
| [format_pattern](format_pattern.md) |  |
| [generated_at](generated_at.md) |  |
| [glossary_term_refs](glossary_term_refs.md) |  |
| [governance_classification](governance_classification.md) |  |
| [grain_entity_refs](grain_entity_refs.md) |  |
| [identifying](identifying.md) |  |
| [implementation_version](implementation_version.md) |  |
| [imports_refs](imports_refs.md) |  |
| [integration_channel](integration_channel.md) |  |
| [integration_class](integration_class.md) |  |
| [integration_level](integration_level.md) |  |
| [integration_ref](integration_ref.md) |  |
| [integration_spec_ref](integration_spec_ref.md) |  |
| [integrity_digest](integrity_digest.md) |  |
| [invariant_refs](invariant_refs.md) |  |
| [key_attribute_refs](key_attribute_refs.md) |  |
| [kind](kind.md) |  |
| [lifecycle_status](lifecycle_status.md) |  |
| [logical_attribute_ref](logical_attribute_ref.md) |  |
| [logical_attribute_refs](logical_attribute_refs.md) |  |
| [logical_entities](logical_entities.md) |  |
| [logical_entity_ref](logical_entity_ref.md) |  |
| [logical_type](logical_type.md) |  |
| [mapping_cardinality](mapping_cardinality.md) |  |
| [mapping_type](mapping_type.md) |  |
| [mappings](mappings.md) |  |
| [master_system](master_system.md) |  |
| [maximum_cardinality](maximum_cardinality.md) |  |
| [measure_attribute_refs](measure_attribute_refs.md) |  |
| [member_system_refs](member_system_refs.md) |  |
| [metric_expression](metric_expression.md) |  |
| [metrics](metrics.md) |  |
| [minimum_cardinality](minimum_cardinality.md) |  |
| [model_package_ref](model_package_ref.md) |  |
| [model_packages](model_packages.md) |  |
| [model_revision](model_revision.md) |  |
| [model_version](model_version.md) |  |
| [multivalued](multivalued.md) |  |
| [name](name.md) |  |
| [namespace](namespace.md) |  |
| [native_name](native_name.md) |  |
| [native_schema_ref](native_schema_ref.md) |  |
| [native_type](native_type.md) |  |
| [object_kind](object_kind.md) |  |
| [ordinal_position](ordinal_position.md) |  |
| [owner_entity_ref](owner_entity_ref.md) |  |
| [owning_unit_ref](owning_unit_ref.md) |  |
| [parent_concept_ref](parent_concept_ref.md) |  |
| [parent_domain_ref](parent_domain_ref.md) |  |
| [physical_field_refs](physical_field_refs.md) |  |
| [physical_fields](physical_fields.md) |  |
| [physical_object_ref](physical_object_ref.md) |  |
| [physical_object_refs](physical_object_refs.md) |  |
| [physical_objects](physical_objects.md) |  |
| [platform_ref](platform_ref.md) |  |
| [policy_binding_id](policy_binding_id.md) |  |
| [policy_bindings](policy_bindings.md) |  |
| [policy_ref](policy_ref.md) |  |
| [policy_refs](policy_refs.md) |  |
| [policy_target_ref](policy_target_ref.md) |  |
| [qualified_name](qualified_name.md) |  |
| [registry_description](registry_description.md) |  |
| [registry_entries](registry_entries.md) |  |
| [registry_id](registry_id.md) |  |
| [registry_name](registry_name.md) |  |
| [registry_status](registry_status.md) |  |
| [relationships](relationships.md) |  |
| [repository_id](repository_id.md) |  |
| [required](required.md) |  |
| [requirement_level](requirement_level.md) |  |
| [requirement_section](requirement_section.md) |  |
| [requirements](requirements.md) |  |
| [schema_path](schema_path.md) |  |
| [selected_attributes](selected_attributes.md) |  |
| [selected_entities](selected_entities.md) |  |
| [selections](selections.md) |  |
| [sensitivity_term_refs](sensitivity_term_refs.md) |  |
| [severity](severity.md) |  |
| [solution_data_role](solution_data_role.md) |  |
| [solution_ref](solution_ref.md) |  |
| [source_artifact_ref](source_artifact_ref.md) |  |
| [source_entity_ref](source_entity_ref.md) |  |
| [source_max_cardinality](source_max_cardinality.md) |  |
| [source_min_cardinality](source_min_cardinality.md) |  |
| [source_model_ref](source_model_ref.md) |  |
| [source_platform_ref](source_platform_ref.md) |  |
| [source_refs](source_refs.md) |  |
| [source_role](source_role.md) |  |
| [source_solution_ref](source_solution_ref.md) |  |
| [source_system_ref](source_system_ref.md) |  |
| [source_uri](source_uri.md) |  |
| [specification_version](specification_version.md) |  |
| [statement](statement.md) | Развёрнутая формулировка требования на понятном языке |
| [system_ref](system_ref.md) |  |
| [tags](tags.md) |  |
| [target_class](target_class.md) | Имя класса LinkML (например LogicalEntity) |
| [target_entity_ref](target_entity_ref.md) |  |
| [target_max_cardinality](target_max_cardinality.md) |  |
| [target_min_cardinality](target_min_cardinality.md) |  |
| [target_path](target_path.md) | JSON Pointer или path hint в теле ModelPackage |
| [target_platform_ref](target_platform_ref.md) |  |
| [target_refs](target_refs.md) |  |
| [target_role](target_role.md) |  |
| [target_slot](target_slot.md) |  |
| [target_solution_ref](target_solution_ref.md) |  |
| [target_system_ref](target_system_ref.md) |  |
| [technology](technology.md) |  |
| [title](title.md) |  |
| [transformation_expression](transformation_expression.md) |  |
| [transformation_mapping_ref](transformation_mapping_ref.md) |  |
| [transformation_mapping_refs](transformation_mapping_refs.md) |  |
| [transformation_ref](transformation_ref.md) |  |
| [unit](unit.md) |  |
| [valid_from](valid_from.md) |  |
| [valid_to](valid_to.md) |  |
| [value_set_ref](value_set_ref.md) |  |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [ApprovalStatusEnum](ApprovalStatusEnum.md) |  |
| [BusinessImportanceEnum](BusinessImportanceEnum.md) |  |
| [CheckSeverityEnum](CheckSeverityEnum.md) |  |
| [CompatibilityModeEnum](CompatibilityModeEnum.md) |  |
| [DataClassEnum](DataClassEnum.md) | Класс данных для наследования модельной спецификацией дата-контракта; не совп... |
| [EnforcementResultEnum](EnforcementResultEnum.md) |  |
| [EntityTypeEnum](EntityTypeEnum.md) | Роль логической сущности в модели решения |
| [FlowDirectionEnum](FlowDirectionEnum.md) |  |
| [FormalCheckKindEnum](FormalCheckKindEnum.md) | Вид формальной проверки в нотации, близкой к LinkML constraints |
| [GovernanceClassificationEnum](GovernanceClassificationEnum.md) | Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными... |
| [IntegrationChannelEnum](IntegrationChannelEnum.md) |  |
| [IntegrationClassEnum](IntegrationClassEnum.md) |  |
| [IntegrationLevelEnum](IntegrationLevelEnum.md) |  |
| [LifecycleStatusEnum](LifecycleStatusEnum.md) |  |
| [LogicalDataTypeEnum](LogicalDataTypeEnum.md) |  |
| [MappingCardinalityEnum](MappingCardinalityEnum.md) |  |
| [MappingTypeEnum](MappingTypeEnum.md) |  |
| [ModelLevelEnum](ModelLevelEnum.md) |  |
| [PhysicalObjectKindEnum](PhysicalObjectKindEnum.md) |  |
| [RequirementLevelEnum](RequirementLevelEnum.md) | Уровень применения требования к спецификации |
| [RequirementSectionEnum](RequirementSectionEnum.md) | Раздел каталога требований (трёхбуквенный код в code) |
| [SolutionDataRoleEnum](SolutionDataRoleEnum.md) |  |
| [SpecificationKindEnum](SpecificationKindEnum.md) |  |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [SemVer](SemVer.md) |  |
| [Sha256Digest](Sha256Digest.md) |  |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
