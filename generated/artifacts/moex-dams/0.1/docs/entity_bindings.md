---
search:
  boost: 5.0
---

# Slot: entity_bindings 

<div data-search-exclude markdown="1">



URI: [dams:entity_bindings](https://data.moex.com/dams/entity_bindings)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataFlowEntityBinding](DataFlowEntityBinding.md) |
| Domain Of | [DataFlow](DataFlow.md) |

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
| self | dams:entity_bindings |
| native | dams:entity_bindings |




## LinkML Source

<details>
```yaml
name: entity_bindings
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: DataFlowEntityBinding
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
