---
search:
  boost: 5.0
---

# Slot: business_importance 

<div data-search-exclude markdown="1">



URI: [dams:business_importance](https://data.moex.com/dams/business_importance)
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
| Range | [BusinessImportanceEnum](BusinessImportanceEnum.md) |
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
| self | dams:business_importance |
| native | dams:business_importance |




## LinkML Source

<details>
```yaml
name: business_importance
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasBusinessClassification
range: BusinessImportanceEnum

```
</details></div>
