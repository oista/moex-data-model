---
search:
  boost: 5.0
---

# Slot: target_platform_ref 

<div data-search-exclude markdown="1">



URI: [dams:target_platform_ref](https://data.moex.com/dams/target_platform_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ITPlatform](ITPlatform.md) |
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
| self | dams:target_platform_ref |
| native | dams:target_platform_ref |




## LinkML Source

<details>
```yaml
name: target_platform_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: ITPlatform
required: true
inlined: false

```
</details></div>
