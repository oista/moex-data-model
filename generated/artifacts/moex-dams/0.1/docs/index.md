# moex_dams



URI: https://data.moex.com/dams/v0.1

Name: moex_dams



## Classes

| Class | Description |
| --- | --- |
| [AccessPoint](AccessPoint.md) | Точка доступа к данным: интерфейс, операция или канал |
| [BusinessDomain](BusinessDomain.md) | Бизнес-домен или предметная область; мастер определяется архитектурным govern... |
| [BusinessProcess](BusinessProcess.md) | Ссылка на бизнес-процесс или его шаг в BPMN-репозитории |
| [ClassificationAssignment](ClassificationAssignment.md) | Версионируемое назначение категории классификации элементу модели с основание... |
| [ConceptualDomain](ConceptualDomain.md) | Концептуальный домен значений: набор смыслов (ValueMeaning) или ссылка на вне... |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |
| [ConceptualProperty](ConceptualProperty.md) | Значимое концептуальное свойство сущности КМД |
| [Contains](Contains.md) | Mixin контейнерности |
| [DataCarrier](DataCarrier.md) | Носитель данных: хранит или передаёт данные (таблица, файл, топик, сообщение ... |
| [DataClassificationTerm](DataClassificationTerm.md) | Специальная категория чувствительности или регулирования, например ПДн или ин... |
| [DataContainer](DataContainer.md) | Контейнер других активов (database, schema, bucket, broker, directory, cluste... |
| [DataContractReference](DataContractReference.md) | Ссылка на дата-контракт в корпоративном дата-каталоге |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и носителями данных модели ... |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |
| [DataStructure](DataStructure.md) | Именованная версия структуры данных: корень дерева SchemaNode с форматом и оп... |
| [DataType](DataType.md) | Корпоративный тип данных: семейство, параметры представления и соответствие X... |
| [Dimension](Dimension.md) | Переиспользуемое аналитическое измерение, связанное с логическими атрибутами |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |
| [EmbeddedElement](EmbeddedElement.md) | Встраиваемый вспомогательный объект без собственного жизненного цикла и глоба... |
| [ExecutionAsset](ExecutionAsset.md) | Исполняемый актив (pipeline / job) с минимальной lineage-ролью |
| [ExternalClassRef](ExternalClassRef.md) | Alignment of a ConceptualEntity to an external class or term (ADR-026) |
| [FormalCheck](FormalCheck.md) | Одна машиночитаемая проверка требования |
| [GlossaryTerm](GlossaryTerm.md) | Термин корпоративного бизнес-глоссария |
| [HasBusinessClassification](HasBusinessClassification.md) | Классификация роли и бизнес-значимости логической сущности |
| [HasDefinition](HasDefinition.md) | Mixin эталонного определения (ADR-025) |
| [HasGovernanceClassification](HasGovernanceClassification.md) | Базовая и специальная классификация чувствительности данных |
| [HasLifecycle](HasLifecycle.md) | Mixin жизненного цикла: статус, период действия и ссылка на заменяющий элемен... |
| [HasLocation](HasLocation.md) | Mixin расположения носителя или точки доступа |
| [HasOwnership](HasOwnership.md) | Mixin владения: data owner, data steward и организационное подразделение |
| [HasPolicyBindings](HasPolicyBindings.md) | Mixin привязки управляемых политик к элементу модели |
| [HasProtocolBinding](HasProtocolBinding.md) | Mixin протокола доступа для точки доступа (AccessPoint) |
| [HasProvenance](HasProvenance.md) | Mixin происхождения и согласования: исходный артефакт, evidence, статус и сог... |
| [HasStructure](HasStructure.md) | Mixin структуры данных носителя |
| [IntegrationReference](IntegrationReference.md) | Ссылка на интеграцию в Clinkr |
| [ITPlatform](ITPlatform.md) | ИТ-платформа; мастер данных — EAM |
| [ITSolution](ITSolution.md) | ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM |
| [ITSystem](ITSystem.md) | ИТ-система; мастер данных — EAM |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности: идентификация, обязательность, кардинальность и ... |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |
| [Mapping](Mapping.md) | Явное соответствие между элементами |
| [Message](Message.md) | Элемент интеграционной модели: сообщение с payload/headers структурами |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |
| [ModelElement](ModelElement.md) | Абстрактный корень иерархии элементов модели: общая идентичность (element_id)... |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных: либо корпоративная conceptual модель (... |
| [ModelSelection](ModelSelection.md) | Переиспользуемый набор выбранных сущностей, атрибутов и физических представле... |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |
| [NativeTypeBinding](NativeTypeBinding.md) | Привязка нативного типа диалекта (SQL, JSON Schema и т |
| [OrganizationUnit](OrganizationUnit.md) | Организационное подразделение |
| [PermissibleValue](PermissibleValue.md) | Допустимое значение внутри ValueDomain (встраиваемый) |
| [Policy](Policy.md) | Политика доступа, хранения, качества или архитектурный инвариант |
| [PolicyBinding](PolicyBinding.md) | Применение управляемой политики к элементу модели |
| [RegistryEntry](RegistryEntry.md) | Локальная ссылочная проекция записи внешней мастер-системы; не является масте... |
| [Relationship](Relationship.md) | Именованная связь между логическими или концептуальными сущностями |
| [RelationTerm](RelationTerm.md) | Governed dictionary term for a conceptual/logical relationship (ADR-026) |
| [RequirementApplicability](RequirementApplicability.md) | Область применимости требования (без graph queries): класс цели, профиль и ур... |
| [RequirementCatalog](RequirementCatalog.md) | Контейнер инстансов SpecificationRequirement вне ModelPackage |
| [Role](Role.md) | Управляемая роль владельца, стюарда, потребителя или согласующего |
| [SchemaNode](SchemaNode.md) | Узел дерева структуры |
| [ScopedDefinition](ScopedDefinition.md) | Контекстное определение элемента модели (ADR-025 / ISO 11179 Context) |
| [SelectedAttribute](SelectedAttribute.md) | Выбранный атрибут и соответствующее физическое поле payload, таблицы или сооб... |
| [SelectedEntity](SelectedEntity.md) | Выбранная для интеграции логическая сущность |
| [SpecificationRequirement](SpecificationRequirement.md) | Нормативное требование к модели, соответствующей reference specification (кат... |
| [TechnicalAsset](TechnicalAsset.md) | Квант данных: адресуемый технический объект управления |
| [ValueDomain](ValueDomain.md) | Представление значений: тип, формат, единица, допустимые значения или ссылка ... |
| [ValueMeaning](ValueMeaning.md) | Смысл допустимого значения внутри ConceptualDomain (встраиваемый, без lifecyc... |
| [ValueSetQuery](ValueSetQuery.md) | Динамический запрос набора значений по образцу LinkML reachable_from (source ... |



## Slots

| Slot | Description |
| --- | --- |
| [access_points](access_points.md) | Коллекция точек доступа пакета (Variant B, ADR-031) |
| [aggregation_function](aggregation_function.md) |  |
| [aliases](aliases.md) |  |
| [alignment_rationale](alignment_rationale.md) | Обоснование статуса выравнивания с концептуальным уровнем |
| [api_version](api_version.md) |  |
| [applicability_id](applicability_id.md) | Stable id for applies_to blocks (e |
| [applies_dams_model_level](applies_dams_model_level.md) |  |
| [applies_implementation_profile](applies_implementation_profile.md) |  |
| [applies_implementation_scope](applies_implementation_scope.md) |  |
| [applies_target_class](applies_target_class.md) | Имя класса LinkML, к экземплярам которого применяется требование |
| [applies_target_kinds](applies_target_kinds.md) | Опциональный allowlist asset_kind / facet (например relational_table, stream_... |
| [applies_to](applies_to.md) | Область применимости требования для formal_checks runner |
| [approval_status](approval_status.md) |  |
| [approved_at](approved_at.md) |  |
| [approved_by_ref](approved_by_ref.md) |  |
| [asset_kind](asset_kind.md) | Разновидность актива |
| [asset_namespace](asset_namespace.md) | Пространство имён источника по аналогии с OpenLineage namespace (например pos... |
| [assignment_id](assignment_id.md) |  |
| [associative](associative.md) |  |
| [attributes](attributes.md) |  |
| [base_type_ref](base_type_ref.md) | Базовый тип, от которого наследуются параметры |
| [binding_id](binding_id.md) |  |
| [binding_ref](binding_ref.md) | Ссылка на внешнее описание binding |
| [broader_domain_ref](broader_domain_ref.md) | Более широкий концептуальный домен |
| [broader_meaning_key](broader_meaning_key.md) | Ключ более широкого ValueMeaning в том же домене |
| [business_importance](business_importance.md) |  |
| [business_key_kind](business_key_kind.md) |  |
| [business_process_refs](business_process_refs.md) |  |
| [cardinality_rationale](cardinality_rationale.md) | Обоснование отсутствия кардинальности для draft/imported связей |
| [carrier_refs](carrier_refs.md) | Носители данных, участвующие в binding (не контейнеры) |
| [catalog_id](catalog_id.md) |  |
| [charset](charset.md) | Кодировка для string/binary |
| [check_id](check_id.md) |  |
| [children](children.md) | local_key дочерних узлов (object / union) |
| [classification_assignments](classification_assignments.md) |  |
| [classification_rationale](classification_rationale.md) |  |
| [classification_source](classification_source.md) |  |
| [classification_term_ref](classification_term_ref.md) |  |
| [classified_element_ref](classified_element_ref.md) |  |
| [code](code.md) |  |
| [column_position](column_position.md) | Позиция колонки (только schema_format=relational; DAMS-валидатор) |
| [compatibility_baseline_ref](compatibility_baseline_ref.md) |  |
| [compatibility_mode](compatibility_mode.md) |  |
| [concept_ref](concept_ref.md) | Опциональная ссылка LogicalAttribute → ConceptualProperty |
| [concept_scheme_uri](concept_scheme_uri.md) | Внешняя схема понятий (SKOS ConceptScheme / онтология) |
| [conceptual_alignment_status](conceptual_alignment_status.md) |  |
| [conceptual_domain_kind](conceptual_domain_kind.md) | Вид концептуального домена (enumerated | described) |
| [conceptual_domain_ref](conceptual_domain_ref.md) | Опциональная ссылка на концептуальный домен смыслов |
| [conceptual_domains](conceptual_domains.md) | Концептуальные домены смыслов (только enterprise-пакеты) |
| [conceptual_entities](conceptual_entities.md) |  |
| [conceptual_entity_refs](conceptual_entity_refs.md) |  |
| [conceptual_implementation_ref](conceptual_implementation_ref.md) | Required for solution packages: reference to the enterprise-conceptual SpecIm... |
| [conceptual_properties](conceptual_properties.md) | Значимые концептуальные свойства (только enterprise-пакеты) |
| [confidence](confidence.md) |  |
| [constraint_expressions](constraint_expressions.md) | Временные выражения ограничений до введения Expression |
| [consumes_refs](consumes_refs.md) |  |
| [containment_kind](containment_kind.md) |  |
| [content_digest](content_digest.md) | Дайджест содержимого структуры (опционально) |
| [content_type](content_type.md) | MIME / content-type сообщения |
| [context_ref](context_ref.md) |  |
| [contract_ref](contract_ref.md) |  |
| [correlation_hint](correlation_hint.md) | Подсказка корреляции (имя поля / путь) |
| [critical_data_element](critical_data_element.md) | Признак критичного элемента данных (CDE) |
| [currency_attribute_ref](currency_attribute_ref.md) | Ссылка на атрибут валюты для денежной величины (Wave 2 soft) |
| [data_carriers](data_carriers.md) | Коллекция носителей данных пакета (Variant B, ADR-031) |
| [data_class](data_class.md) |  |
| [data_containers](data_containers.md) | Коллекция контейнеров пакета (Variant B, ADR-031) |
| [data_flows](data_flows.md) |  |
| [data_format](data_format.md) | Wire-формат носителя (parquet, csv, json); не путать с schema_format |
| [data_model_bindings](data_model_bindings.md) |  |
| [data_owner_ref](data_owner_ref.md) |  |
| [data_steward_ref](data_steward_ref.md) |  |
| [data_structures](data_structures.md) | Коллекция структур данных пакета |
| [data_type_ref](data_type_ref.md) | Ссылка на корпоративный DataType |
| [data_types](data_types.md) | Корпоративный реестр типов данных |
| [datatype_timezone_policy](datatype_timezone_policy.md) | Политика часового пояса для date/time/datetime типов |
| [default_relationship_kind](default_relationship_kind.md) | Optional default relationship_kind when this term is used |
| [default_value](default_value.md) |  |
| [definition_rationale](definition_rationale.md) | Human rationale for declaring an own definition when a source is also cited, ... |
| [definition_source_ref](definition_source_ref.md) | Reference to the element or external term whose definition is inherited or ad... |
| [dependency_kind](dependency_kind.md) | Required when entity_tier=dependent |
| [depends_on_refs](depends_on_refs.md) | Owner conceptual entities this dependent entity requires |
| [deprecated_by_ref](deprecated_by_ref.md) |  |
| [derived_expression](derived_expression.md) |  |
| [description](description.md) |  |
| [diagnostic_code](diagnostic_code.md) | Мост к DAMS-STRUCT-* / DAMS-REF-* / DAMS-REQ-* |
| [dialect](dialect.md) | Диалект/платформа нативного типа (postgresql, oracle, json, …) |
| [dialect_native_type](dialect_native_type.md) | Имя нативного типа в диалекте |
| [dimension_attribute_refs](dimension_attribute_refs.md) |  |
| [dimensions](dimensions.md) |  |
| [direction](direction.md) |  |
| [domain_contexts](domain_contexts.md) |  |
| [domain_ref](domain_ref.md) |  |
| [domain_refs](domain_refs.md) |  |
| [dynamic_query](dynamic_query.md) | Динамический запрос набора (reachable_from) |
| [element_id](element_id.md) |  |
| [entity_bindings](entity_bindings.md) |  |
| [entity_tier](entity_tier.md) | Structural independence of the conceptual entity (ADR-026) |
| [entity_type](entity_type.md) |  |
| [envelope_kind](envelope_kind.md) | Вид конверта (none, cloudevents, custom) |
| [envelope_ref](envelope_ref.md) | Ссылка на описание конверта (для custom / профиля) |
| [evidence_refs](evidence_refs.md) |  |
| [execution_assets](execution_assets.md) | Коллекция исполняемых активов пакета (Variant B, ADR-031) |
| [expression](expression.md) | Имя фиксированного шаблона для conditional_branch / custom (например ldm006_a... |
| [external_class_ref_id](external_class_ref_id.md) |  |
| [external_class_refs](external_class_refs.md) | Canonical ConceptualEntity → external class/term alignments with match_kind (... |
| [external_specification_ref](external_specification_ref.md) | Optional ExternalSpecification / version pin (ADR-020) |
| [filter_expression](filter_expression.md) |  |
| [flow_ref](flow_ref.md) |  |
| [foreign_key_target](foreign_key_target.md) | Цель внешнего ключа как structure_id#local_key (только relational) |
| [formal_checks](formal_checks.md) |  |
| [format_pattern](format_pattern.md) | Шаблон/формат значения для ValueDomain (regex или маска) |
| [forward_label](forward_label.md) | Natural-language label source → target (ADR-026) |
| [forward_label_en](forward_label_en.md) | English forward label (ADR-026) |
| [generated_at](generated_at.md) |  |
| [genesis_kind](genesis_kind.md) | external = aligns to ontology/external class(es); native = modelled without e... |
| [glossary_term_refs](glossary_term_refs.md) |  |
| [governance_classification](governance_classification.md) |  |
| [grain_entity_refs](grain_entity_refs.md) |  |
| [headers_structure_ref](headers_structure_ref.md) | Структура заголовков сообщения |
| [http_method](http_method.md) |  |
| [identifying](identifying.md) |  |
| [identity_rule](identity_rule.md) | Деловое правило идентичности экземпляров сущности в контексте ИТ-решения |
| [implementation_scope](implementation_scope.md) | Body-level scope: enterprise (no solution_ref) or solution |
| [implementation_status](implementation_status.md) | Статус реализации требования |
| [implementation_version](implementation_version.md) |  |
| [imports_refs](imports_refs.md) |  |
| [include_self](include_self.md) | Включать стартовые узлы в результат |
| [integration_channel](integration_channel.md) |  |
| [integration_class](integration_class.md) |  |
| [integration_level](integration_level.md) |  |
| [integration_ref](integration_ref.md) |  |
| [integration_spec_ref](integration_spec_ref.md) |  |
| [integrity_digest](integrity_digest.md) |  |
| [interface_ref](interface_ref.md) | Родительский интерфейс для операции (asset_kind=operation) |
| [invariant_refs](invariant_refs.md) |  |
| [inverse_label](inverse_label.md) | Natural-language label target → source |
| [inverse_label_en](inverse_label_en.md) | English inverse label (ADR-026) |
| [is_identifying](is_identifying.md) | Является ли свойство идентифицирующим (бизнес-ключ) |
| [is_primary_key](is_primary_key.md) | Признак первичного ключа (только relational; DAMS-валидатор) |
| [is_unique](is_unique.md) | Признак уникальности колонки (только relational; DAMS-валидатор) |
| [isolation_rationale](isolation_rationale.md) | Обоснование семантической изоляции сущности (LDM-007) |
| [item_node](item_node.md) | local_key узла элемента массива или значения map |
| [key_attribute_refs](key_attribute_refs.md) |  |
| [kind](kind.md) |  |
| [lifecycle_status](lifecycle_status.md) |  |
| [lineage_role](lineage_role.md) | Роль актива в lineage (source, sink, intermediate, none) |
| [linkml_type](linkml_type.md) | Имя типа LinkML (string, integer, …) |
| [local_key](local_key.md) | Локальный ключ узла внутри DataStructure |
| [location_uri](location_uri.md) |  |
| [logical_attribute_ref](logical_attribute_ref.md) |  |
| [logical_attribute_refs](logical_attribute_refs.md) |  |
| [logical_entities](logical_entities.md) |  |
| [logical_entity_ref](logical_entity_ref.md) |  |
| [lossiness](lossiness.md) | Оценка потери точности при отображении |
| [mapping_cardinality](mapping_cardinality.md) |  |
| [mapping_coverage_status](mapping_coverage_status.md) | Статус покрытия элемента mapping’ом на соседнем уровне модели (logical ↔ phys... |
| [mapping_rationale](mapping_rationale.md) | Обоснование для planned / technical-only / not-applicable / inherited |
| [mapping_type](mapping_type.md) |  |
| [mappings](mappings.md) |  |
| [master_system](master_system.md) |  |
| [match_kind](match_kind.md) | Alignment strength |
| [max_length](max_length.md) | Максимальная длина для string/binary |
| [max_occurs](max_occurs.md) | Максимальная кратность; без верхней границы слот отсутствует |
| [max_value](max_value.md) | Максимальное допустимое значение (described) |
| [maximum_cardinality](maximum_cardinality.md) |  |
| [meaning_definition](meaning_definition.md) | Определение смысла (skos:definition) |
| [meaning_key](meaning_key.md) | Ключ смысла, уникальный внутри ConceptualDomain |
| [meaning_label](meaning_label.md) | Предпочтительная метка смысла (skos:prefLabel в OWL-проекции) |
| [meaning_status](meaning_status.md) | Статус смысла значения |
| [meaning_term_ref](meaning_term_ref.md) | CURIE внешнего термина, уточняющего смысл |
| [measure_attribute_refs](measure_attribute_refs.md) |  |
| [member_system_refs](member_system_refs.md) |  |
| [message_refs](message_refs.md) | Сообщения точки доступа |
| [messages](messages.md) | Коллекция сообщений пакета (интеграционная модель) |
| [metric_expression](metric_expression.md) |  |
| [metrics](metrics.md) |  |
| [min_length](min_length.md) | Минимальная длина для string/binary |
| [min_occurs](min_occurs.md) | Минимальная кратность |
| [min_value](min_value.md) | Минимальное допустимое значение (described) |
| [minimum_cardinality](minimum_cardinality.md) |  |
| [model_package_ref](model_package_ref.md) |  |
| [model_packages](model_packages.md) |  |
| [model_revision](model_revision.md) |  |
| [model_version](model_version.md) |  |
| [multivalued](multivalued.md) |  |
| [name](name.md) |  |
| [namespace](namespace.md) |  |
| [native_name](native_name.md) |  |
| [native_type](native_type.md) |  |
| [native_type_bindings](native_type_bindings.md) | Привязки нативных типов диалектов к DataType |
| [node_kind](node_kind.md) | Вид узла (scalar, object, array, map, union, enum, reference) |
| [nodes](nodes.md) | Плоский список узлов структуры |
| [nullable](nullable.md) | Допустимость null (отдельно от required) |
| [ontology_property_ref](ontology_property_ref.md) | Optional owl:ObjectProperty IRI |
| [operation_name](operation_name.md) |  |
| [ordinal](ordinal.md) | Порядок значения в перечислении |
| [ordinal_position](ordinal_position.md) |  |
| [owner_entity_ref](owner_entity_ref.md) | Structural parent LogicalEntity of this attribute (containment), not the data... |
| [ownership_inheritance_rule](ownership_inheritance_rule.md) | Deprecated as source of truth (ADR-023) |
| [owning_unit_ref](owning_unit_ref.md) |  |
| [parameter_mapping](parameter_mapping.md) | Описание отображения параметров (precision/scale/length) |
| [parent_concept_ref](parent_concept_ref.md) |  |
| [parent_domain_ref](parent_domain_ref.md) |  |
| [parent_ref](parent_ref.md) | Родитель в контейнерной иерархии (без циклов) |
| [path_template](path_template.md) |  |
| [payload_structure_ref](payload_structure_ref.md) | Структура тела сообщения |
| [permissible_values](permissible_values.md) | Встроенный список допустимых значений |
| [platform_ref](platform_ref.md) |  |
| [policy_binding_id](policy_binding_id.md) |  |
| [policy_bindings](policy_bindings.md) |  |
| [policy_ref](policy_ref.md) |  |
| [policy_refs](policy_refs.md) |  |
| [policy_target_ref](policy_target_ref.md) |  |
| [precision](precision.md) | Точность для decimal (общее число цифр) |
| [previous_version_ref](previous_version_ref.md) | Предыдущая версия этой структуры |
| [produces_refs](produces_refs.md) |  |
| [property_kind](property_kind.md) | Вид концептуального свойства |
| [property_owner_entity_ref](property_owner_entity_ref.md) | ConceptualEntity-владелец ConceptualProperty (концептуальный containment) |
| [protocol](protocol.md) | Протокол доступа (например https, jdbc, kafka) |
| [protocol_version](protocol_version.md) |  |
| [qualified_name](qualified_name.md) |  |
| [rationale](rationale.md) | Why this scoped wording differs from the reference definition |
| [realizes_attribute_ref](realizes_attribute_ref.md) | Опциональная связь с логическим атрибутом (как concept_ref) |
| [reference_target](reference_target.md) | Цель для node_kind=reference (другая DataStructure или узел) |
| [region](region.md) |  |
| [registry_description](registry_description.md) |  |
| [registry_entries](registry_entries.md) |  |
| [registry_id](registry_id.md) |  |
| [registry_name](registry_name.md) |  |
| [registry_status](registry_status.md) |  |
| [relation_term_ref](relation_term_ref.md) | Reference to a governed RelationTerm providing forward/inverse labels (ADR-02... |
| [relation_terms](relation_terms.md) | Governed relation-term dictionary for the package (ADR-026) |
| [relation_to_reference](relation_to_reference.md) |  |
| [relationship_kind](relationship_kind.md) | Тип логической связи (Wave 2) |
| [relationship_types](relationship_types.md) | Типы связей для обхода |
| [relationships](relationships.md) |  |
| [remediation](remediation.md) | Actionable remediation text for CI / Cursor / authors |
| [repository_id](repository_id.md) |  |
| [required](required.md) |  |
| [requirement_level](requirement_level.md) |  |
| [requirement_section](requirement_section.md) |  |
| [requirements](requirements.md) |  |
| [root_local_key](root_local_key.md) | local_key корневого узла в nodes |
| [scale](scale.md) | Масштаб для decimal (число цифр после запятой); scale ≤ precision |
| [schema_dialect](schema_dialect.md) | Диалект / версия языка схемы (JSON Schema dialect IRI, AsyncAPI format id) |
| [schema_format](schema_format.md) | Формат схемы (стартовый enum; реестр форматов — отдельная задача) |
| [schema_node_refs](schema_node_refs.md) | Ссылки на узлы схемы (SchemaNode) в DataStructure |
| [scope_kind](scope_kind.md) |  |
| [scope_ref](scope_ref.md) | Target of the scope (e |
| [scoped_definition_id](scoped_definition_id.md) |  |
| [scoped_definitions](scoped_definitions.md) | Context-scoped definitions (ADR-025); v1 scope_kind = system |
| [security_classification](security_classification.md) | Режим защиты (Wave 2); ортогонален governance_classification |
| [selected_attributes](selected_attributes.md) |  |
| [selected_entities](selected_entities.md) |  |
| [selection_ref](selection_ref.md) | Optional ExternalTermSelection id (ADR-020) |
| [selections](selections.md) |  |
| [sensitivity_term_refs](sensitivity_term_refs.md) |  |
| [serves_refs](serves_refs.md) | Носители, доступные через эту точку доступа |
| [severity](severity.md) |  |
| [significance_basis](significance_basis.md) | Основания существования ConceptualProperty (минимум одно) |
| [significance_rationale](significance_rationale.md) | Обязательное обоснование, если significance_basis содержит explicit_decision |
| [solution_data_role](solution_data_role.md) |  |
| [solution_ref](solution_ref.md) |  |
| [source_artifact_ref](source_artifact_ref.md) |  |
| [source_entity_ref](source_entity_ref.md) |  |
| [source_kind](source_kind.md) | Kind of external source (ontology, corp architecture, …) |
| [source_max_cardinality](source_max_cardinality.md) |  |
| [source_min_cardinality](source_min_cardinality.md) |  |
| [source_model_ref](source_model_ref.md) |  |
| [source_nodes](source_nodes.md) | Стартовые узлы reachable_from |
| [source_ontology](source_ontology.md) | IRI/CURIE исходной онтологии для динамического набора |
| [source_platform_ref](source_platform_ref.md) |  |
| [source_pointer](source_pointer.md) | JSON Pointer или аналог внутри source_artifact_ref |
| [source_refs](source_refs.md) |  |
| [source_role](source_role.md) |  |
| [source_solution_ref](source_solution_ref.md) |  |
| [source_system_ref](source_system_ref.md) |  |
| [source_uri](source_uri.md) |  |
| [specification_version](specification_version.md) |  |
| [statement](statement.md) | Полная нормативная формулировка на русском для человека: без имён LinkML-клас... |
| [structure_ref](structure_ref.md) | Ссылка на структуру данных (DataStructure, ADR-038) |
| [structure_version](structure_version.md) | Версия структуры (SemVer) |
| [superseded_by](superseded_by.md) | Ссылка на требование, которым данное заменено (при lifecycle_status=supersede... |
| [symmetric](symmetric.md) | When true, forward and inverse labels are the same; inverse_label may be omit... |
| [system_ref](system_ref.md) |  |
| [tags](tags.md) |  |
| [target_class](target_class.md) | Имя класса LinkML (например LogicalEntity) |
| [target_entity_ref](target_entity_ref.md) |  |
| [target_max_cardinality](target_max_cardinality.md) |  |
| [target_min_cardinality](target_min_cardinality.md) |  |
| [target_path](target_path.md) | JSON Pointer или path hint в теле ModelPackage |
| [target_platform_ref](target_platform_ref.md) |  |
| [target_ref](target_ref.md) | IRI/CURIE of the external class or term (ADR-026) |
| [target_refs](target_refs.md) |  |
| [target_role](target_role.md) |  |
| [target_slot](target_slot.md) |  |
| [target_slots](target_slots.md) | Список слотов для kind=at_least_one_slots |
| [target_solution_ref](target_solution_ref.md) |  |
| [target_system_ref](target_system_ref.md) |  |
| [technology](technology.md) |  |
| [temporal_semantics](temporal_semantics.md) | Семантика даты/времени (Wave 2 soft) |
| [term_direction](term_direction.md) | Whether this Relationship assertion uses the forward or inverse wording of re... |
| [text](text.md) | Scoped definition text (skos:definition in this context) |
| [timezone_policy](timezone_policy.md) | Политика часового пояса для timestamp (Wave 2 soft) |
| [title](title.md) |  |
| [transformation_expression](transformation_expression.md) |  |
| [transformation_mapping_ref](transformation_mapping_ref.md) |  |
| [transformation_mapping_refs](transformation_mapping_refs.md) |  |
| [transformation_ref](transformation_ref.md) |  |
| [type_family](type_family.md) | Семейство типа (boolean, integer, decimal, …) |
| [type_name](type_name.md) | Каноническое имя типа в корпоративном реестре |
| [unit](unit.md) |  |
| [unit_code](unit_code.md) | Код единицы измерения (UCUM / корпоративный код) для ValueDomain |
| [valid_from](valid_from.md) |  |
| [valid_to](valid_to.md) |  |
| [value_code](value_code.md) | Код значения, уникальный внутри ValueDomain |
| [value_definition](value_definition.md) | Определение допустимого значения |
| [value_domain_kind](value_domain_kind.md) | Вид домена значений (enumerated | described | reference_set) |
| [value_domain_ref](value_domain_ref.md) | Ссылка на домен представления значений |
| [value_domains](value_domains.md) | Домены представления значений (enterprise или solution) |
| [value_label](value_label.md) | Метка допустимого значения |
| [value_meaning_key](value_meaning_key.md) | Ключ ValueMeaning в связанном ConceptualDomain |
| [value_meanings](value_meanings.md) | Встроенный список смыслов значений |
| [value_set_query_id](value_set_query_id.md) | Локальный идентификатор динамического запроса внутри ValueDomain |
| [value_set_source](value_set_source.md) | Внешний источник набора значений (reference_set) |
| [value_status](value_status.md) | Статус допустимого значения |
| [xsd_datatype](xsd_datatype.md) | Соответствующий XSD datatype (например xsd:string) |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [AccessPointKindEnum](AccessPointKindEnum.md) |  |
| [ApprovalStatusEnum](ApprovalStatusEnum.md) |  |
| [BusinessImportanceEnum](BusinessImportanceEnum.md) | Важность сущности в модели решения (не criticality бизнес-процесса) |
| [BusinessKeyKindEnum](BusinessKeyKindEnum.md) | Характер бизнес-ключа логической сущности |
| [CheckSeverityEnum](CheckSeverityEnum.md) |  |
| [CompatibilityModeEnum](CompatibilityModeEnum.md) |  |
| [ConceptualAlignmentStatusEnum](ConceptualAlignmentStatusEnum.md) | Статус выравнивания логической сущности с корпоративным концептуальным уровне... |
| [ConceptualDomainKindEnum](ConceptualDomainKindEnum.md) | Вид концептуального домена (ISO 11179 Conceptual Domain) |
| [ContainmentKindEnum](ContainmentKindEnum.md) |  |
| [DAMSModelLevelEnum](DAMSModelLevelEnum.md) | Package-level DAMS model layer (ADR-021) |
| [DataCarrierKindEnum](DataCarrierKindEnum.md) |  |
| [DataClassEnum](DataClassEnum.md) | Класс данных для наследования модельной спецификацией дата-контракта; не совп... |
| [DataContainerKindEnum](DataContainerKindEnum.md) |  |
| [DefinitionScopeKindEnum](DefinitionScopeKindEnum.md) | Kind of scope for a ScopedDefinition (ADR-025) |
| [DependencyKindEnum](DependencyKindEnum.md) | Kind of structural dependency for a dependent ConceptualEntity (ADR-026) |
| [EnforcementResultEnum](EnforcementResultEnum.md) |  |
| [EntityTierEnum](EntityTierEnum.md) | Structural independence of a ConceptualEntity (ADR-026) |
| [EntityTypeEnum](EntityTypeEnum.md) | Роль логической сущности в модели решения |
| [EnvelopeKindEnum](EnvelopeKindEnum.md) | Вид конверта сообщения (Message |
| [ExecutionAssetKindEnum](ExecutionAssetKindEnum.md) |  |
| [ExternalMatchKindEnum](ExternalMatchKindEnum.md) | Strength of ConceptualEntity ↔ external class alignment (ADR-026) |
| [ExternalSourceKindEnum](ExternalSourceKindEnum.md) | Kind of external source for a ConceptualEntity alignment (ADR-026) |
| [FlowDirectionEnum](FlowDirectionEnum.md) |  |
| [FormalCheckKindEnum](FormalCheckKindEnum.md) | Вид формальной проверки в нотации, близкой к LinkML constraints |
| [GenesisKindEnum](GenesisKindEnum.md) | Whether a ConceptualEntity is aligned to an external class/term or is native ... |
| [GovernanceClassificationEnum](GovernanceClassificationEnum.md) | Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными... |
| [ImplementationProfileEnum](ImplementationProfileEnum.md) | DAMS-side mirror of kernel ImplementationProfile for ModelPackage metadata |
| [ImplementationScopeEnum](ImplementationScopeEnum.md) |  |
| [IntegrationChannelEnum](IntegrationChannelEnum.md) |  |
| [IntegrationClassEnum](IntegrationClassEnum.md) |  |
| [IntegrationLevelEnum](IntegrationLevelEnum.md) |  |
| [LifecycleStatusEnum](LifecycleStatusEnum.md) |  |
| [LineageRoleEnum](LineageRoleEnum.md) |  |
| [LogicalDataTypeEnum](LogicalDataTypeEnum.md) |  |
| [LossinessEnum](LossinessEnum.md) | Оценка потери точности NativeTypeBinding |
| [MappingCardinalityEnum](MappingCardinalityEnum.md) |  |
| [MappingCoverageStatusEnum](MappingCoverageStatusEnum.md) | Статус покрытия элемента mapping’ом на соседнем уровне модели (logical ↔ phys... |
| [MappingTypeEnum](MappingTypeEnum.md) | Kind of Mapping assertion |
| [ModelLevelEnum](ModelLevelEnum.md) |  |
| [PropertyKindEnum](PropertyKindEnum.md) | Вид концептуального свойства |
| [RelationshipKindEnum](RelationshipKindEnum.md) | Тип логической связи (Wave 2) |
| [RequirementImplementationStatus](RequirementImplementationStatus.md) | Статус реализации утверждённого требования |
| [RequirementLevelEnum](RequirementLevelEnum.md) | Уровень применения требования к спецификации |
| [RequirementLifecycleStatus](RequirementLifecycleStatus.md) | Статус жизненного цикла нормативного требования (SpecificationRequirement) |
| [RequirementSectionEnum](RequirementSectionEnum.md) | Раздел каталога требований (трёхбуквенный код в code) |
| [SchemaFormatEnum](SchemaFormatEnum.md) | Формат схемы DataStructure (стартовый набор; перенос в реестр — отдельно) |
| [SchemaNodeKindEnum](SchemaNodeKindEnum.md) | Вид узла SchemaNode |
| [ScopedDefinitionRelationEnum](ScopedDefinitionRelationEnum.md) | How a scoped definition relates to the element's reference definition (ADR-02... |
| [SecurityClassificationEnum](SecurityClassificationEnum.md) | Режим защиты данных (Wave 2); ортогонален governance_classification |
| [SignificanceBasisEnum](SignificanceBasisEnum.md) | Основание существования ConceptualProperty в КМД (вариант B) |
| [SolutionDataRoleEnum](SolutionDataRoleEnum.md) |  |
| [SpecificationKindEnum](SpecificationKindEnum.md) |  |
| [TermDirectionEnum](TermDirectionEnum.md) | Which side of a RelationTerm a Relationship assertion uses (ADR-026) |
| [TimezonePolicyEnum](TimezonePolicyEnum.md) | Политика часового пояса для временных DataType |
| [TypeFamilyEnum](TypeFamilyEnum.md) | Семейство корпоративного DataType |
| [ValueDomainKindEnum](ValueDomainKindEnum.md) | Вид домена представления значений (ISO 11179 Value Domain) |


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
