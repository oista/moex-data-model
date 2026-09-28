---
search:
  boost: 5.0
---

# Slot: physical_field_refs 

<div data-search-exclude markdown="1">



URI: [dams:physical_field_refs](https://data.moex.com/dams/physical_field_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | Связь потока с логическими сущностями, атрибутами и физическими объектами мод... |  no  |
| [SelectedAttribute](SelectedAttribute.md) | Выбранный атрибут и соответствующее физическое поле payload, таблицы или сооб... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalField](PhysicalField.md) |
| Domain Of | [DataFlowEntityBinding](DataFlowEntityBinding.md), [SelectedAttribute](SelectedAttribute.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:physical_field_refs |
| native | dams:physical_field_refs |




## LinkML Source

<details>
```yaml
name: physical_field_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DataFlowEntityBinding
- SelectedAttribute
range: PhysicalField
multivalued: true
inlined: false

```
</details></div>
