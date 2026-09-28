---
search:
  boost: 5.0
---

# Slot: qualified_name 

<div data-search-exclude markdown="1">



URI: [dams:qualified_name](https://data.moex.com/dams/qualified_name)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
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
| self | dams:qualified_name |
| native | dams:qualified_name |




## LinkML Source

<details>
```yaml
name: qualified_name
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalObject
range: string
required: true

```
</details></div>
