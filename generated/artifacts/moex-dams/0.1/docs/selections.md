---
search:
  boost: 5.0
---

# Slot: selections 

<div data-search-exclude markdown="1">



URI: [dams:selections](https://data.moex.com/dams/selections)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ModelSelection](ModelSelection.md) |
| Domain Of | [DataModelBinding](DataModelBinding.md) |

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
| self | dams:selections |
| native | dams:selections |




## LinkML Source

<details>
```yaml
name: selections
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataModelBinding
range: ModelSelection
multivalued: true
inlined: true
inlined_as_list: true
minimum_cardinality: 1

```
</details></div>
