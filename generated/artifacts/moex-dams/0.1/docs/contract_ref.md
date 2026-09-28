---
search:
  boost: 5.0
---

# Slot: contract_ref 

<div data-search-exclude markdown="1">



URI: [dams:contract_ref](https://data.moex.com/dams/contract_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataContractReference](DataContractReference.md) |
| Domain Of | [DataFlow](DataFlow.md), [DataModelBinding](DataModelBinding.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:contract_ref |
| native | dams:contract_ref |




## LinkML Source

<details>
```yaml
name: contract_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
- DataModelBinding
range: DataContractReference
inlined: false

```
</details></div>
