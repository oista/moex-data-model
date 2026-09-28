---
search:
  boost: 5.0
---

# Slot: repository_id 

<div data-search-exclude markdown="1">



URI: [dams:repository_id](https://data.moex.com/dams/repository_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uriorcurie](Uriorcurie.md) |
| Domain Of | [MOEXModelRepository](MOEXModelRepository.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:repository_id |
| native | dams:repository_id |




## LinkML Source

<details>
```yaml
name: repository_id
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
identifier: true
domain_of:
- MOEXModelRepository
range: uriorcurie
required: true

```
</details></div>
