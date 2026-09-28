---
search:
  boost: 5.0
---

# Slot: dimension_attribute_refs 

<div data-search-exclude markdown="1">



URI: [dams:dimension_attribute_refs](https://data.moex.com/dams/dimension_attribute_refs)
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
| Range | [LogicalAttribute](LogicalAttribute.md) |
| Domain Of | [Metric](Metric.md), [Dimension](Dimension.md) |

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
| self | dams:dimension_attribute_refs |
| native | dams:dimension_attribute_refs |




## LinkML Source

<details>
```yaml
name: dimension_attribute_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- Metric
- Dimension
range: LogicalAttribute
multivalued: true
inlined: false

```
</details></div>
