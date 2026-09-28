---
search:
  boost: 5.0
---

# Slot: formal_checks 

<div data-search-exclude markdown="1">



URI: [dams:formal_checks](https://data.moex.com/dams/formal_checks)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SpecificationRequirement](SpecificationRequirement.md) | Нормативное требование к модели, соответствующей reference specification (кат... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [FormalCheck](FormalCheck.md) |
| Domain Of | [SpecificationRequirement](SpecificationRequirement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
| Minimum Cardinality | 1 |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:formal_checks |
| native | dams:formal_checks |




## LinkML Source

<details>
```yaml
name: formal_checks
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- SpecificationRequirement
range: FormalCheck
multivalued: true
inlined: true
inlined_as_list: true
minimum_cardinality: 1

```
</details></div>
