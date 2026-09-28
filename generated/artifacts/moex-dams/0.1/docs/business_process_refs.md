---
search:
  boost: 5.0
---

# Slot: business_process_refs 

<div data-search-exclude markdown="1">



URI: [dams:business_process_refs](https://data.moex.com/dams/business_process_refs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [BusinessProcess](BusinessProcess.md) |
| Domain Of | [DomainContext](DomainContext.md) |

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
| self | dams:business_process_refs |
| native | dams:business_process_refs |




## LinkML Source

<details>
```yaml
name: business_process_refs
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DomainContext
range: BusinessProcess
multivalued: true
inlined: false

```
</details></div>
