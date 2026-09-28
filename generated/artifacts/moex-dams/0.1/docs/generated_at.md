---
search:
  boost: 5.0
---

# Slot: generated_at 

<div data-search-exclude markdown="1">



URI: [dams:generated_at](https://data.moex.com/dams/generated_at)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Datetime](Datetime.md) |
| Domain Of | [DataModelBinding](DataModelBinding.md) |

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
| self | dams:generated_at |
| native | dams:generated_at |




## LinkML Source

<details>
```yaml
name: generated_at
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataModelBinding
range: datetime
required: true

```
</details></div>
