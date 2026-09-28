---
search:
  boost: 5.0
---

# Slot: integration_level 

<div data-search-exclude markdown="1">



URI: [dams:integration_level](https://data.moex.com/dams/integration_level)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [IntegrationLevelEnum](IntegrationLevelEnum.md) |
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
| self | dams:integration_level |
| native | dams:integration_level |




## LinkML Source

<details>
```yaml
name: integration_level
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: IntegrationLevelEnum
required: true

```
</details></div>
