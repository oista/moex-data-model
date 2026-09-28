---
search:
  boost: 5.0
---

# Slot: classification_assignments 

<div data-search-exclude markdown="1">



URI: [dams:classification_assignments](https://data.moex.com/dams/classification_assignments)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MOEXModelRepository](MOEXModelRepository.md) | Корневой контейнер для проверки набора моделей, ссылочных проекций справочник... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ClassificationAssignment](ClassificationAssignment.md) |
| Domain Of | [MOEXModelRepository](MOEXModelRepository.md) |

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
| self | dams:classification_assignments |
| native | dams:classification_assignments |




## LinkML Source

<details>
```yaml
name: classification_assignments
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- MOEXModelRepository
range: ClassificationAssignment
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
