---
search:
  boost: 5.0
---

# Slot: physical_objects 

<div data-search-exclude markdown="1">



URI: [dams:physical_objects](https://data.moex.com/dams/physical_objects)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ModelPackage](ModelPackage.md) | Версионируемый артефакт модели данных одного ИТ-решения или корпоративной мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalObject](PhysicalObject.md) |
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
| self | dams:physical_objects |
| native | dams:physical_objects |




## LinkML Source

<details>
```yaml
name: physical_objects
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ModelPackage
range: PhysicalObject
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
