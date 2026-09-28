---
search:
  boost: 5.0
---

# Slot: owning_unit_ref 

<div data-search-exclude markdown="1">



URI: [dams:owning_unit_ref](https://data.moex.com/dams/owning_unit_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [HasOwnership](HasOwnership.md) | Mixin владения: data owner, data steward и организационное подразделение |  no  |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |  no  |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [OrganizationUnit](OrganizationUnit.md) |
| Domain Of | [HasOwnership](HasOwnership.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:owning_unit_ref |
| native | dams:owning_unit_ref |




## LinkML Source

<details>
```yaml
name: owning_unit_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasOwnership
range: OrganizationUnit
inlined: false

```
</details></div>
