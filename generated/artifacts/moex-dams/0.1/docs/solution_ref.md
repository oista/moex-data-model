---
search:
  boost: 5.0
---

# Slot: solution_ref 

<div data-search-exclude markdown="1">



URI: [dams:solution_ref](https://data.moex.com/dams/solution_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ITSolution](ITSolution.md) |
| Domain Of | [ModelPackage](ModelPackage.md), [DomainContext](DomainContext.md), [LogicalEntity](LogicalEntity.md), [PhysicalObject](PhysicalObject.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:solution_ref |
| native | dams:solution_ref |




## LinkML Source

<details>
```yaml
name: solution_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelPackage
- DomainContext
- LogicalEntity
- PhysicalObject
range: ITSolution
inlined: false

```
</details></div>
