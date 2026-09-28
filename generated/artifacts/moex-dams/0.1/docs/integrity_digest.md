---
search:
  boost: 5.0
---

# Slot: integrity_digest 

<div data-search-exclude markdown="1">



URI: [dams:integrity_digest](https://data.moex.com/dams/integrity_digest)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Sha256Digest](Sha256Digest.md) |
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
| self | dams:integrity_digest |
| native | dams:integrity_digest |




## LinkML Source

<details>
```yaml
name: integrity_digest
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataModelBinding
range: Sha256Digest
required: true

```
</details></div>
