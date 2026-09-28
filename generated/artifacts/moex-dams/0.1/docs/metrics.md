---
search:
  boost: 5.0
---

# Slot: metrics 

<div data-search-exclude markdown="1">



URI: [dams:metrics](https://data.moex.com/dams/metrics)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Metric](Metric.md) |
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
| self | dams:metrics |
| native | dams:metrics |




## LinkML Source

<details>
```yaml
name: metrics
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: Metric
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
