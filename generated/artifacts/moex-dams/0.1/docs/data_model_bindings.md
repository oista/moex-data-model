---
search:
  boost: 5.0
---

# Slot: data_model_bindings 

<div data-search-exclude markdown="1">



URI: [dams:data_model_bindings](https://data.moex.com/dams/data_model_bindings)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataModelBinding](DataModelBinding.md) |
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
| self | dams:data_model_bindings |
| native | dams:data_model_bindings |




## LinkML Source

<details>
```yaml
name: data_model_bindings
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: DataModelBinding
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
