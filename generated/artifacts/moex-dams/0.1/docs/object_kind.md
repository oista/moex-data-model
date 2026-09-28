---
search:
  boost: 5.0
---

# Slot: object_kind 

<div data-search-exclude markdown="1">



URI: [dams:object_kind](https://data.moex.com/dams/object_kind)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalObjectKindEnum](PhysicalObjectKindEnum.md) |
| Domain Of | [PhysicalObject](PhysicalObject.md) |

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
| self | dams:object_kind |
| native | dams:object_kind |




## LinkML Source

<details>
```yaml
name: object_kind
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalObject
range: PhysicalObjectKindEnum
required: true

```
</details></div>
