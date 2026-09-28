---
search:
  boost: 5.0
---

# Slot: approval_status 

<div data-search-exclude markdown="1">



URI: [dams:approval_status](https://data.moex.com/dams/approval_status)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ClassificationAssignment](ClassificationAssignment.md) | Версионируемое назначение категории классификации элементу модели с основание... |  no  |
| [PolicyBinding](PolicyBinding.md) | Применение управляемой политики к элементу модели |  no  |
| [HasProvenance](HasProvenance.md) | Mixin происхождения и согласования: исходный артефакт, evidence, статус и сог... |  no  |
| [Mapping](Mapping.md) | Явное соответствие между элементами концептуального, логического и физическог... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ApprovalStatusEnum](ApprovalStatusEnum.md) |
| Domain Of | [ClassificationAssignment](ClassificationAssignment.md), [PolicyBinding](PolicyBinding.md), [HasProvenance](HasProvenance.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:approval_status |
| native | dams:approval_status |




## LinkML Source

<details>
```yaml
name: approval_status
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ClassificationAssignment
- PolicyBinding
- HasProvenance
range: ApprovalStatusEnum

```
</details></div>
