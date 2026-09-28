---
search:
  boost: 5.0
---

# Slot: glossary_term_refs 

<div data-search-exclude markdown="1">



URI: [dams:glossary_term_refs](https://data.moex.com/dams/glossary_term_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelElement](ModelElement.md) | Абстрактный корень иерархии элементов модели: общая идентичность (element_id)... |  no  |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |  no  |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |  no  |
| [Relationship](Relationship.md) | Именованная связь между логическими или концептуальными сущностями |  no  |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |
| [PhysicalField](PhysicalField.md) | Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute |  no  |
| [Mapping](Mapping.md) | Явное соответствие между элементами концептуального, логического и физическог... |  no  |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |
| [ModelSelection](ModelSelection.md) | Переиспользуемый набор выбранных сущностей, атрибутов и физических представле... |  no  |
| [SelectedEntity](SelectedEntity.md) | Выбранная для интеграции логическая сущность |  no  |
| [SelectedAttribute](SelectedAttribute.md) | Выбранный атрибут и соответствующее физическое поле payload, таблицы или сооб... |  no  |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |
| [Dimension](Dimension.md) | Переиспользуемое аналитическое измерение, связанное с логическими атрибутами |  no  |
| [SpecificationRequirement](SpecificationRequirement.md) | Нормативное требование к модели, соответствующей reference specification (кат... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [GlossaryTerm](GlossaryTerm.md) |
| Domain Of | [ModelElement](ModelElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:glossary_term_refs |
| native | dams:glossary_term_refs |




## LinkML Source

<details>
```yaml
name: glossary_term_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelElement
range: GlossaryTerm
multivalued: true
inlined: false

```
</details></div>
