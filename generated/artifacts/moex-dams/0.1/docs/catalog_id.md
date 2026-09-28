---
search:
  boost: 5.0
---

# Slot: catalog_id 

<div data-search-exclude markdown="1">



URI: [dams:catalog_id](https://data.moex.com/dams/catalog_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RequirementCatalog](RequirementCatalog.md) | Контейнер инстансов SpecificationRequirement вне ModelPackage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uriorcurie](Uriorcurie.md) |
| Domain Of | [RequirementCatalog](RequirementCatalog.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:catalog_id |
| native | dams:catalog_id |




## LinkML Source

<details>
```yaml
name: catalog_id
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
identifier: true
domain_of:
- RequirementCatalog
range: uriorcurie
required: true

```
</details></div>
