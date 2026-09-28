---
search:
  boost: 5.0
---

# Slot: classification_rationale 

<div data-search-exclude markdown="1">



URI: [dams:classification_rationale](https://data.moex.com/dams/classification_rationale)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ClassificationAssignment](ClassificationAssignment.md) | Версионируемое назначение категории классификации элементу модели с основание... |  no  |
| [HasGovernanceClassification](HasGovernanceClassification.md) | Базовая и специальная классификация чувствительности данных |  no  |
| [LogicalEntity](LogicalEntity.md) | Представление бизнес-сущности в доменном контексте и модели конкретного решен... |  no  |
| [LogicalAttribute](LogicalAttribute.md) | Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и класси... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ClassificationAssignment](ClassificationAssignment.md), [HasGovernanceClassification](HasGovernanceClassification.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:classification_rationale |
| native | dams:classification_rationale |




## LinkML Source

<details>
```yaml
name: classification_rationale
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ClassificationAssignment
- HasGovernanceClassification
range: string

```
</details></div>
