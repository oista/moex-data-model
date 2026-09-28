---
search:
  boost: 5.0
---

# Slot: code 

<div data-search-exclude markdown="1">



URI: [dams:code](https://data.moex.com/dams/code)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SpecificationRequirement](SpecificationRequirement.md) | Нормативное требование к модели, соответствующей reference specification (кат... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SpecificationRequirement](SpecificationRequirement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:code |
| native | dams:code |




## LinkML Source

<details>
```yaml
name: code
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- SpecificationRequirement
range: string
required: true
pattern: ^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$

```
</details></div>
