---
search:
  boost: 5.0
---

# Slot: requirements 

<div data-search-exclude markdown="1">



URI: [dams:requirements](https://data.moex.com/dams/requirements)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RequirementCatalog](RequirementCatalog.md) | Контейнер инстансов SpecificationRequirement вне ModelPackage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SpecificationRequirement](SpecificationRequirement.md) |
| Domain Of | [RequirementCatalog](RequirementCatalog.md) |

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
| self | dams:requirements |
| native | dams:requirements |




## LinkML Source

<details>
```yaml
name: requirements
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- RequirementCatalog
range: SpecificationRequirement
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
