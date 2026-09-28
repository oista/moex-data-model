---
search:
  boost: 5.0
---

# Slot: flow_ref 

<div data-search-exclude markdown="1">



URI: [dams:flow_ref](https://data.moex.com/dams/flow_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataFlow](DataFlow.md) |
| Domain Of | [DataFlowEntityBinding](DataFlowEntityBinding.md) |

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
| self | dams:flow_ref |
| native | dams:flow_ref |




## LinkML Source

<details>
```yaml
name: flow_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlowEntityBinding
range: DataFlow
required: true
inlined: false

```
</details></div>
