---
search:
  boost: 5.0
---

# Slot: attributes 

<div data-search-exclude markdown="1">



URI: [dams:attributes](https://data.moex.com/dams/attributes)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LogicalAttribute](LogicalAttribute.md) |
| Domain Of | [LogicalEntity](LogicalEntity.md) |

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
| self | dams:attributes |
| native | dams:attributes |




## LinkML Source

<details>
```yaml
name: attributes
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- LogicalEntity
range: LogicalAttribute
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
