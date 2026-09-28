---
search:
  boost: 5.0
---

# Slot: key_attribute_refs 

<div data-search-exclude markdown="1">



URI: [dams:key_attribute_refs](https://data.moex.com/dams/key_attribute_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptualEntity](ConceptualEntity.md) | Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реали... |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uriorcurie](Uriorcurie.md) |
| Domain Of | [ConceptualEntity](ConceptualEntity.md), [LogicalEntity](LogicalEntity.md) |

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
| self | dams:key_attribute_refs |
| native | dams:key_attribute_refs |




## LinkML Source

<details>
```yaml
name: key_attribute_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ConceptualEntity
- LogicalEntity
range: uriorcurie
multivalued: true

```
</details></div>
