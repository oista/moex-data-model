---
search:
  boost: 5.0
---

# Slot: physical_object_ref 

<div data-search-exclude markdown="1">



URI: [dams:physical_object_ref](https://data.moex.com/dams/physical_object_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalField](PhysicalField.md) | Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalObject](PhysicalObject.md) |
| Domain Of | [PhysicalField](PhysicalField.md) |

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
| self | dams:physical_object_ref |
| native | dams:physical_object_ref |




## LinkML Source

<details>
```yaml
name: physical_object_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalField
range: PhysicalObject
required: true
inlined: false

```
</details></div>
