---
search:
  boost: 5.0
---

# Slot: source_model_ref 

<div data-search-exclude markdown="1">



URI: [dams:source_model_ref](https://data.moex.com/dams/source_model_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uri](Uri.md) |
| Domain Of | [DataFlowEntityBinding](DataFlowEntityBinding.md) |

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
| self | dams:source_model_ref |
| native | dams:source_model_ref |




## LinkML Source

<details>
```yaml
name: source_model_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlowEntityBinding
range: uri
required: true

```
</details></div>
