---
search:
  boost: 5.0
---

# Slot: relationships 

<div data-search-exclude markdown="1">



URI: [dams:relationships](https://data.moex.com/dams/relationships)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Relationship](Relationship.md) |
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
| self | dams:relationships |
| native | dams:relationships |




## LinkML Source

<details>
```yaml
name: relationships
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelPackage
range: Relationship
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
