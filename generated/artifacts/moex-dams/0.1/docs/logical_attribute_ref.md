---
search:
  boost: 5.0
---

# Slot: logical_attribute_ref 

<div data-search-exclude markdown="1">



URI: [dams:logical_attribute_ref](https://data.moex.com/dams/logical_attribute_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SelectedAttribute](SelectedAttribute.md) | Выбранный атрибут и соответствующее физическое поле payload, таблицы или сооб... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LogicalAttribute](LogicalAttribute.md) |
| Domain Of | [SelectedAttribute](SelectedAttribute.md) |

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
| self | dams:logical_attribute_ref |
| native | dams:logical_attribute_ref |




## LinkML Source

<details>
```yaml
name: logical_attribute_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- SelectedAttribute
range: LogicalAttribute
required: true
inlined: false

```
</details></div>
