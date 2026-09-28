---
search:
  boost: 5.0
---

# Slot: check_id 

<div data-search-exclude markdown="1">



URI: [dams:check_id](https://data.moex.com/dams/check_id)
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
| self | dams:check_id |
| native | dams:check_id |




## LinkML Source

<details>
```yaml
name: check_id
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
identifier: true
domain_of:
- FormalCheck
range: string
required: true

```
</details></div>
