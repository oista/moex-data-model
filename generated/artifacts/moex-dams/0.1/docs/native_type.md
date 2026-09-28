---
search:
  boost: 5.0
---

# Slot: native_type 

<div data-search-exclude markdown="1">



URI: [dams:native_type](https://data.moex.com/dams/native_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalField](PhysicalField.md) | Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
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
| self | dams:native_type |
| native | dams:native_type |




## LinkML Source

<details>
```yaml
name: native_type
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalField
range: string
required: true

```
</details></div>
