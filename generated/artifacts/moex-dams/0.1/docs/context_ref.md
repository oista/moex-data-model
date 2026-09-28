---
search:
  boost: 5.0
---

# Slot: context_ref 

<div data-search-exclude markdown="1">



URI: [dams:context_ref](https://data.moex.com/dams/context_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DomainContext](DomainContext.md) |
| Domain Of | [LogicalEntity](LogicalEntity.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:context_ref |
| native | dams:context_ref |




## LinkML Source

<details>
```yaml
name: context_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- LogicalEntity
range: DomainContext
required: true
inlined: false

```
</details></div>
