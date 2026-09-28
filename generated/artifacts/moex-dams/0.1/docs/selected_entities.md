---
search:
  boost: 5.0
---

# Slot: selected_entities 

<div data-search-exclude markdown="1">



URI: [dams:selected_entities](https://data.moex.com/dams/selected_entities)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelSelection](ModelSelection.md) | Переиспользуемый набор выбранных сущностей, атрибутов и физических представле... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SelectedEntity](SelectedEntity.md) |
| Domain Of | [ModelSelection](ModelSelection.md) |

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
| self | dams:selected_entities |
| native | dams:selected_entities |




## LinkML Source

<details>
```yaml
name: selected_entities
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelSelection
range: SelectedEntity
multivalued: true
inlined: true
inlined_as_list: true
minimum_cardinality: 1

```
</details></div>
