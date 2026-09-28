---
search:
  boost: 5.0
---

# Slot: metric_expression 

<div data-search-exclude markdown="1">



URI: [dams:metric_expression](https://data.moex.com/dams/metric_expression)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Metric](Metric.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:metric_expression |
| native | dams:metric_expression |




## LinkML Source

<details>
```yaml
name: metric_expression
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- Metric
range: string
required: true

```
</details></div>
