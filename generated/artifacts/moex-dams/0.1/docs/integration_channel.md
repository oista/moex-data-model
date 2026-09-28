---
search:
  boost: 5.0
---

# Slot: integration_channel 

<div data-search-exclude markdown="1">



URI: [dams:integration_channel](https://data.moex.com/dams/integration_channel)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [IntegrationChannelEnum](IntegrationChannelEnum.md) |
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
| self | dams:integration_channel |
| native | dams:integration_channel |




## LinkML Source

<details>
```yaml
name: integration_channel
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: IntegrationChannelEnum
required: true

```
</details></div>
