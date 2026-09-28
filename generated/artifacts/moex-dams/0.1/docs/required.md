---
search:
  boost: 5.0
---

# Slot: required 

<div data-search-exclude markdown="1">



URI: [dams:required](https://data.moex.com/dams/required)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |  no  |
| [PhysicalField](PhysicalField.md) | Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [LogicalAttribute](LogicalAttribute.md), [PhysicalField](PhysicalField.md) |

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
| self | dams:required |
| native | dams:required |




## LinkML Source

<details>
```yaml
name: required
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- LogicalAttribute
- PhysicalField
range: boolean
required: true

```
</details></div>
