---
search:
  boost: 5.0
---

# Slot: physical_fields 

<div data-search-exclude markdown="1">



URI: [dams:physical_fields](https://data.moex.com/dams/physical_fields)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalField](PhysicalField.md) |
| Domain Of | [PhysicalObject](PhysicalObject.md) |

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
| self | dams:physical_fields |
| native | dams:physical_fields |




## LinkML Source

<details>
```yaml
name: physical_fields
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalObject
range: PhysicalField
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
