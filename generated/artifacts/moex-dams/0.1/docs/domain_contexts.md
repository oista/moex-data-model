---
search:
  boost: 5.0
---

# Slot: domain_contexts 

<div data-search-exclude markdown="1">



URI: [dams:domain_contexts](https://data.moex.com/dams/domain_contexts)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DomainContext](DomainContext.md) |
| Domain Of | [ModelPackage](ModelPackage.md) |

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
| self | dams:domain_contexts |
| native | dams:domain_contexts |




## LinkML Source

<details>
```yaml
name: domain_contexts
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelPackage
range: DomainContext
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
