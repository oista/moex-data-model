---
search:
  boost: 5.0
---

# Slot: evidence_refs 

<div data-search-exclude markdown="1">



URI: [dams:evidence_refs](https://data.moex.com/dams/evidence_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [HasProvenance](HasProvenance.md) | Mixin происхождения и согласования: исходный артефакт, evidence, статус и сог... |  no  |
| [Mapping](Mapping.md) | Явное соответствие между элементами концептуального, логического и физическог... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Uri](Uri.md) |
| Domain Of | [HasProvenance](HasProvenance.md) |

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
| self | dams:evidence_refs |
| native | dams:evidence_refs |




## LinkML Source

<details>
```yaml
name: evidence_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- HasProvenance
range: uri
multivalued: true

```
</details></div>
