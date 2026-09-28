---
search:
  boost: 5.0
---

# Slot: integration_ref 

<div data-search-exclude markdown="1">



URI: [dams:integration_ref](https://data.moex.com/dams/integration_ref)
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
| Range | [IntegrationReference](IntegrationReference.md) |
| Domain Of | [DataFlow](DataFlow.md), [DataModelBinding](DataModelBinding.md) |

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
| self | dams:integration_ref |
| native | dams:integration_ref |




## LinkML Source

<details>
```yaml
name: integration_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
- DataModelBinding
range: IntegrationReference
required: true
inlined: false

```
</details></div>
