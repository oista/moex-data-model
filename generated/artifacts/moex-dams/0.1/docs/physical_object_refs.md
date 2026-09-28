---
search:
  boost: 5.0
---

# Slot: physical_object_refs 

<div data-search-exclude markdown="1">



URI: [dams:physical_object_refs](https://data.moex.com/dams/physical_object_refs)
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
| Range | [PhysicalObject](PhysicalObject.md) |
| Domain Of | [DataFlowEntityBinding](DataFlowEntityBinding.md), [SelectedEntity](SelectedEntity.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
| Minimum Cardinality | 1 |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:physical_object_refs |
| native | dams:physical_object_refs |




## LinkML Source

<details>
```yaml
name: physical_object_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlowEntityBinding
- SelectedEntity
range: PhysicalObject
multivalued: true
inlined: false
minimum_cardinality: 1

```
</details></div>
