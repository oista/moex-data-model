---
search:
  boost: 5.0
---

# Slot: system_ref 

<div data-search-exclude markdown="1">



URI: [dams:system_ref](https://data.moex.com/dams/system_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ITSystem](ITSystem.md) |
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
| self | dams:system_ref |
| native | dams:system_ref |




## LinkML Source

<details>
```yaml
name: system_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalObject
range: ITSystem
required: true
inlined: false

```
</details></div>
