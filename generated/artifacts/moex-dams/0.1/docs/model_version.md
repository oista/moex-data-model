---
search:
  boost: 5.0
---

# Slot: model_version 

<div data-search-exclude markdown="1">



URI: [dams:model_version](https://data.moex.com/dams/model_version)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |
| [DataModelBinding](DataModelBinding.md) | Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую реви... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SemVer](SemVer.md) |
| Domain Of | [ModelPackage](ModelPackage.md), [DataModelBinding](DataModelBinding.md) |

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
| self | dams:model_version |
| native | dams:model_version |




## LinkML Source

<details>
```yaml
name: model_version
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelPackage
- DataModelBinding
range: SemVer
required: true

```
</details></div>
