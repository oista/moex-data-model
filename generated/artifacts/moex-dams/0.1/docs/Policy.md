---
search:
  boost: 10.0
---

# Class: Policy 


_Политика доступа, хранения, качества или архитектурный инвариант._



<div data-search-exclude markdown="1">



URI: [dams:Policy](https://data.moex.com/dams/Policy)





```mermaid
 classDiagram
    class Policy
    click Policy href "../Policy/"
      RegistryEntry <|-- Policy
        click RegistryEntry href "../RegistryEntry/"
      
      Policy : master_system
        
      Policy : registry_description
        
      Policy : registry_id
        
      Policy : registry_name
        
      Policy : registry_status
        
          
    
        
        
        Policy --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      Policy : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **Policy**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [registry_id](registry_id.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_name](registry_name.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_description](registry_description.md) | 0..1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [master_system](master_system.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [source_uri](source_uri.md) | 0..1 <br/> [Uri](Uri.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_status](registry_status.md) | 1 <br/> [LifecycleStatusEnum](LifecycleStatusEnum.md) |  | [RegistryEntry](RegistryEntry.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [PolicyBinding](PolicyBinding.md) | [policy_ref](policy_ref.md) | range | [Policy](Policy.md) |
| [HasPolicyBindings](HasPolicyBindings.md) | [policy_refs](policy_refs.md) | range | [Policy](Policy.md) |
| [LogicalEntity](LogicalEntity.md) | [invariant_refs](invariant_refs.md) | range | [Policy](Policy.md) |
| [LogicalEntity](LogicalEntity.md) | [policy_refs](policy_refs.md) | range | [Policy](Policy.md) |
| [LogicalAttribute](LogicalAttribute.md) | [policy_refs](policy_refs.md) | range | [Policy](Policy.md) |
| [PhysicalObject](PhysicalObject.md) | [policy_refs](policy_refs.md) | range | [Policy](Policy.md) |
| [Metric](Metric.md) | [policy_refs](policy_refs.md) | range | [Policy](Policy.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:Policy |
| native | dams:Policy |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Policy
description: Политика доступа, хранения, качества или архитектурный инвариант.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: Policy
description: Политика доступа, хранения, качества или архитектурный инвариант.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: Policy
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Policy
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Policy
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Policy
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Policy
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Policy
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
