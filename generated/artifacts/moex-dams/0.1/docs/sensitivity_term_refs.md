---
search:
  boost: 5.0
---

# Slot: sensitivity_term_refs 

<div data-search-exclude markdown="1">



URI: [dams:sensitivity_term_refs](https://data.moex.com/dams/sensitivity_term_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [HasGovernanceClassification](HasGovernanceClassification.md) | Базовая и специальная классификация чувствительности данных |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DataClassificationTerm](DataClassificationTerm.md) |
| Domain Of | [HasGovernanceClassification](HasGovernanceClassification.md) |

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
| self | dams:sensitivity_term_refs |
| native | dams:sensitivity_term_refs |




## LinkML Source

<details>
```yaml
name: sensitivity_term_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasGovernanceClassification
range: DataClassificationTerm
multivalued: true
inlined: false

```
</details></div>
