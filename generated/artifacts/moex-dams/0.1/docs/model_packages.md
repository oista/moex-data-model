---
search:
  boost: 5.0
---

# Slot: model_packages 

<div data-search-exclude markdown="1">



URI: [dams:model_packages](https://data.moex.com/dams/model_packages)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ModelPackage](ModelPackage.md) |
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
| self | dams:model_packages |
| native | dams:model_packages |




## LinkML Source

<details>
```yaml
name: model_packages
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: ModelPackage
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
