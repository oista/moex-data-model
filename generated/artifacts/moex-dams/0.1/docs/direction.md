---
search:
  boost: 5.0
---

# Slot: direction 

<div data-search-exclude markdown="1">



URI: [dams:direction](https://data.moex.com/dams/direction)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [FlowDirectionEnum](FlowDirectionEnum.md) |
| Domain Of | [PhysicalObject](PhysicalObject.md), [DataFlowEntityBinding](DataFlowEntityBinding.md) |

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
| self | dams:direction |
| native | dams:direction |




## LinkML Source

<details>
```yaml
name: direction
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PhysicalObject
- DataFlowEntityBinding
range: FlowDirectionEnum
required: true

```
</details></div>
