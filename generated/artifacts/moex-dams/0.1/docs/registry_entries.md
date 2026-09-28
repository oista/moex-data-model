---
search:
  boost: 5.0
---

# Slot: registry_entries 

<div data-search-exclude markdown="1">



URI: [dams:registry_entries](https://data.moex.com/dams/registry_entries)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [RegistryEntry](RegistryEntry.md) |
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
| self | dams:registry_entries |
| native | dams:registry_entries |




## LinkML Source

<details>
```yaml
name: registry_entries
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: RegistryEntry
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
