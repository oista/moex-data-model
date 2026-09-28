---
search:
  boost: 5.0
---

# Slot: policy_bindings 

<div data-search-exclude markdown="1">



URI: [dams:policy_bindings](https://data.moex.com/dams/policy_bindings)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PolicyBinding](PolicyBinding.md) |
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
| self | dams:policy_bindings |
| native | dams:policy_bindings |




## LinkML Source

<details>
```yaml
name: policy_bindings
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: PolicyBinding
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
