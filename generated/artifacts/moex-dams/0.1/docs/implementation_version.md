---
search:
  boost: 5.0
---

# Slot: implementation_version 

<div data-search-exclude markdown="1">



URI: [dams:implementation_version](https://data.moex.com/dams/implementation_version)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SemVer](SemVer.md) |
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
| self | dams:implementation_version |
| native | dams:implementation_version |




## LinkML Source

<details>
```yaml
name: implementation_version
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataModelBinding
range: SemVer
required: true

```
</details></div>
