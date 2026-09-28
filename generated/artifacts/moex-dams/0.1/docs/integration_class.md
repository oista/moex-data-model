---
search:
  boost: 5.0
---

# Slot: integration_class 

<div data-search-exclude markdown="1">



URI: [dams:integration_class](https://data.moex.com/dams/integration_class)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlow](DataFlow.md) | Ссылочная проекция зарегистрированной интеграции; топология и канал являются ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [IntegrationClassEnum](IntegrationClassEnum.md) |
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
| self | dams:integration_class |
| native | dams:integration_class |




## LinkML Source

<details>
```yaml
name: integration_class
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlow
range: IntegrationClassEnum
required: true

```
</details></div>
