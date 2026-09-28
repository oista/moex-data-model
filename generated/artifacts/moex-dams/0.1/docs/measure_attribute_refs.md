---
search:
  boost: 5.0
---

# Slot: measure_attribute_refs 

<div data-search-exclude markdown="1">



URI: [dams:measure_attribute_refs](https://data.moex.com/dams/measure_attribute_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LogicalAttribute](LogicalAttribute.md) |
| Domain Of | [Metric](Metric.md) |

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
| self | dams:measure_attribute_refs |
| native | dams:measure_attribute_refs |




## LinkML Source

<details>
```yaml
name: measure_attribute_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- Metric
range: LogicalAttribute
multivalued: true
inlined: false
minimum_cardinality: 1

```
</details></div>
