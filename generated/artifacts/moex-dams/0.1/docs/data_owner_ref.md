---
search:
  boost: 5.0
---

# Slot: data_owner_ref 

<div data-search-exclude markdown="1">



URI: [dams:data_owner_ref](https://data.moex.com/dams/data_owner_ref)
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
| Range | [Role](Role.md) |
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
| self | dams:data_owner_ref |
| native | dams:data_owner_ref |




## LinkML Source

<details>
```yaml
name: data_owner_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasOwnership
range: Role
inlined: false

```
</details></div>
