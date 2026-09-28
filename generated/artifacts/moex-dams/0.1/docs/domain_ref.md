---
search:
  boost: 5.0
---

# Slot: domain_ref 

<div data-search-exclude markdown="1">



URI: [dams:domain_ref](https://data.moex.com/dams/domain_ref)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DomainContext](DomainContext.md) | Ограниченный логический контекст с собственной терминологией и областью ответ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [BusinessDomain](BusinessDomain.md) |
| Domain Of | [DomainContext](DomainContext.md) |

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
| self | dams:domain_ref |
| native | dams:domain_ref |




## LinkML Source

<details>
```yaml
name: domain_ref
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- DomainContext
range: BusinessDomain
required: true
inlined: false

```
</details></div>
