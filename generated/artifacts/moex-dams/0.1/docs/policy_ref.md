---
search:
  boost: 5.0
---

# Slot: policy_ref 

<div data-search-exclude markdown="1">



URI: [dams:policy_ref](https://data.moex.com/dams/policy_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PolicyBinding](PolicyBinding.md) | Применение управляемой политики к элементу модели |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Policy](Policy.md) |
| Domain Of | [PolicyBinding](PolicyBinding.md) |

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
| self | dams:policy_ref |
| native | dams:policy_ref |




## LinkML Source

<details>
```yaml
name: policy_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- PolicyBinding
range: Policy
required: true
inlined: false

```
</details></div>
