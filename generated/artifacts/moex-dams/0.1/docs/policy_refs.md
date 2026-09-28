---
search:
  boost: 5.0
---

# Slot: policy_refs 

<div data-search-exclude markdown="1">



URI: [dams:policy_refs](https://data.moex.com/dams/policy_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [HasPolicyBindings](HasPolicyBindings.md) | Mixin привязки управляемых политик к элементу модели |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |  no  |
| [PhysicalObject](PhysicalObject.md) | Квант данных или техническая точка публикации/потребления |  no  |
| [Metric](Metric.md) | Управляемое определение бизнес- или технической метрики; является опциональны... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Policy](Policy.md) |
| Domain Of | [HasPolicyBindings](HasPolicyBindings.md) |

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
| self | dams:policy_refs |
| native | dams:policy_refs |




## LinkML Source

<details>
```yaml
name: policy_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasPolicyBindings
range: Policy
multivalued: true
inlined: false

```
</details></div>
