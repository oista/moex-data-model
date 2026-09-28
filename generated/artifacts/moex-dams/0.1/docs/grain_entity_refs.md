---
search:
  boost: 5.0
---

# Slot: grain_entity_refs 

<div data-search-exclude markdown="1">



URI: [dams:grain_entity_refs](https://data.moex.com/dams/grain_entity_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |
| [Dimension](Dimension.md) | Переиспользуемое аналитическое измерение, связанное с логическими атрибутами |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LogicalEntity](LogicalEntity.md) |
| Domain Of | [Metric](Metric.md), [Dimension](Dimension.md) |

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
| self | dams:grain_entity_refs |
| native | dams:grain_entity_refs |




## LinkML Source

<details>
```yaml
name: grain_entity_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- Metric
- Dimension
range: LogicalEntity
multivalued: true
inlined: false
minimum_cardinality: 1

```
</details></div>
