---
search:
  boost: 5.0
---

# Slot: logical_entity_ref 

<div data-search-exclude markdown="1">



URI: [dams:logical_entity_ref](https://data.moex.com/dams/logical_entity_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |
| [SelectedEntity](SelectedEntity.md) | Выбранная для интеграции логическая сущность |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LogicalEntity](LogicalEntity.md) |
| Domain Of | [DataFlowEntityBinding](DataFlowEntityBinding.md), [SelectedEntity](SelectedEntity.md) |

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
| self | dams:logical_entity_ref |
| native | dams:logical_entity_ref |




## LinkML Source

<details>
```yaml
name: logical_entity_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlowEntityBinding
- SelectedEntity
range: LogicalEntity
required: true
inlined: false

```
</details></div>
