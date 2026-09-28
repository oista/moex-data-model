---
search:
  boost: 5.0
---

# Slot: governance_classification 

<div data-search-exclude markdown="1">



URI: [dams:governance_classification](https://data.moex.com/dams/governance_classification)
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
| Range | [GovernanceClassificationEnum](GovernanceClassificationEnum.md) |
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
| self | dams:governance_classification |
| native | dams:governance_classification |




## LinkML Source

<details>
```yaml
name: governance_classification
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- ClassificationAssignment
- HasGovernanceClassification
range: GovernanceClassificationEnum

```
</details></div>
