---
search:
  boost: 5.0
---

# Slot: severity 

<div data-search-exclude markdown="1">



URI: [dams:severity](https://data.moex.com/dams/severity)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FormalCheck](FormalCheck.md) | Одна машиночитаемая проверка требования |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [CheckSeverityEnum](CheckSeverityEnum.md) |
| Domain Of | [FormalCheck](FormalCheck.md) |

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
| self | dams:severity |
| native | dams:severity |




## LinkML Source

<details>
```yaml
name: severity
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- FormalCheck
range: CheckSeverityEnum
required: true

```
</details></div>
