---
search:
  boost: 5.0
---

# Slot: source_system_ref 

<div data-search-exclude markdown="1">



URI: [dams:source_system_ref](https://data.moex.com/dams/source_system_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ITSystem](ITSystem.md) |
| Domain Of | [DataFlow](DataFlow.md) |

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
| self | dams:source_system_ref |
| native | dams:source_system_ref |




## LinkML Source

<details>
```yaml
name: source_system_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: ITSystem
required: true
inlined: false

```
</details></div>
