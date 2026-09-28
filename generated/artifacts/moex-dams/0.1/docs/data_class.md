---
search:
  boost: 5.0
---

# Slot: data_class 

<div data-search-exclude markdown="1">



URI: [dams:data_class](https://data.moex.com/dams/data_class)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [HasBusinessClassification](HasBusinessClassification.md) | Классификация роли и бизнес-значимости логической сущности |  no  |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataClassEnum](DataClassEnum.md) |
| Domain Of | [HasBusinessClassification](HasBusinessClassification.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:data_class |
| native | dams:data_class |




## LinkML Source

<details>
```yaml
name: data_class
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasBusinessClassification
range: DataClassEnum

```
</details></div>
