---
search:
  boost: 5.0
---

# Slot: selected_attributes 

<div data-search-exclude markdown="1">



URI: [dams:selected_attributes](https://data.moex.com/dams/selected_attributes)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SelectedEntity](SelectedEntity.md) | Выбранная для интеграции логическая сущность |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SelectedAttribute](SelectedAttribute.md) |
| Domain Of | [SelectedEntity](SelectedEntity.md) |

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
| self | dams:selected_attributes |
| native | dams:selected_attributes |




## LinkML Source

<details>
```yaml
name: selected_attributes
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- SelectedEntity
range: SelectedAttribute
multivalued: true
inlined: true
inlined_as_list: true
minimum_cardinality: 1

```
</details></div>
