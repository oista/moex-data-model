---
search:
  boost: 5.0
---

# Slot: member_system_refs 

<div data-search-exclude markdown="1">



URI: [dams:member_system_refs](https://data.moex.com/dams/member_system_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ITSolution](ITSolution.md) | ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ITSystem](ITSystem.md) |
| Domain Of | [ITSolution](ITSolution.md) |

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
| self | dams:member_system_refs |
| native | dams:member_system_refs |




## LinkML Source

<details>
```yaml
name: member_system_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ITSolution
range: ITSystem
multivalued: true
inlined: false

```
</details></div>
