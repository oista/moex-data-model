---
search:
  boost: 5.0
---

# Slot: dimensions 

<div data-search-exclude markdown="1">



URI: [dams:dimensions](https://data.moex.com/dams/dimensions)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Dimension](Dimension.md) |
| Domain Of | [MOEXModelRepository](MOEXModelRepository.md) |

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
| self | dams:dimensions |
| native | dams:dimensions |




## LinkML Source

<details>
```yaml
name: dimensions
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: Dimension
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
