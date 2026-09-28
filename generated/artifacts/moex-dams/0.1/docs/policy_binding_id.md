---
search:
  boost: 5.0
---

# Slot: policy_binding_id 

<div data-search-exclude markdown="1">



URI: [dams:policy_binding_id](https://data.moex.com/dams/policy_binding_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PolicyBinding](PolicyBinding.md) | Применение управляемой политики к элементу модели |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uriorcurie](Uriorcurie.md) |
| Domain Of | [PolicyBinding](PolicyBinding.md) |

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
| self | dams:policy_binding_id |
| native | dams:policy_binding_id |




## LinkML Source

<details>
```yaml
name: policy_binding_id
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
identifier: true
domain_of:
- PolicyBinding
range: uriorcurie
required: true

```
</details></div>
