---
search:
  boost: 5.0
---

# Slot: diagnostic_code 


_Мост к DAMS-STRUCT-* / DAMS-REF-* / будущим DAMS-REQ-*._



<div data-search-exclude markdown="1">



URI: [dams:diagnostic_code](https://data.moex.com/dams/diagnostic_code)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FormalCheck](FormalCheck.md) | Одна машиночитаемая проверка требования |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [FormalCheck](FormalCheck.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:diagnostic_code |
| native | dams:diagnostic_code |




## LinkML Source

<details>
```yaml
name: diagnostic_code
description: Мост к DAMS-STRUCT-* / DAMS-REF-* / будущим DAMS-REQ-*.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- FormalCheck
range: string

```
</details></div>
