---
search:
  boost: 10.0
---

# Class: BusinessDomain 


_Бизнес-домен или предметная область; мастер определяется архитектурным governance._



<div data-search-exclude markdown="1">



URI: [dams:BusinessDomain](https://data.moex.com/dams/BusinessDomain)





```mermaid
 classDiagram
    class BusinessDomain
    click BusinessDomain href "../BusinessDomain/"
      RegistryEntry <|-- BusinessDomain
        click RegistryEntry href "../RegistryEntry/"
      
      BusinessDomain : master_system
        
      BusinessDomain : parent_domain_ref
        
          
    
        
        
        BusinessDomain --> "0..1" BusinessDomain : parent_domain_ref
        click BusinessDomain href "../BusinessDomain/"
    

        
      BusinessDomain : registry_description
        
      BusinessDomain : registry_id
        
      BusinessDomain : registry_name
        
      BusinessDomain : registry_status
        
          
    
        
        
        BusinessDomain --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      BusinessDomain : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **BusinessDomain**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [parent_domain_ref](parent_domain_ref.md) | 0..1 <br/> [BusinessDomain](BusinessDomain.md) |  | direct |
| [registry_id](registry_id.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_name](registry_name.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_description](registry_description.md) | 0..1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [master_system](master_system.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [source_uri](source_uri.md) | 0..1 <br/> [Uri](Uri.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_status](registry_status.md) | 1 <br/> [LifecycleStatusEnum](LifecycleStatusEnum.md) |  | [RegistryEntry](RegistryEntry.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [BusinessDomain](BusinessDomain.md) | [parent_domain_ref](parent_domain_ref.md) | range | [BusinessDomain](BusinessDomain.md) |
| [ModelPackage](ModelPackage.md) | [domain_refs](domain_refs.md) | range | [BusinessDomain](BusinessDomain.md) |
| [DomainContext](DomainContext.md) | [domain_ref](domain_ref.md) | range | [BusinessDomain](BusinessDomain.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:BusinessDomain |
| native | dams:BusinessDomain |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: BusinessDomain
description: Бизнес-домен или предметная область; мастер определяется архитектурным
  governance.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
slots:
- parent_domain_ref

```
</details>

### Induced

<details>
```yaml
name: BusinessDomain
description: Бизнес-домен или предметная область; мастер определяется архитектурным
  governance.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  parent_domain_ref:
    name: parent_domain_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - BusinessDomain
    range: BusinessDomain
    inlined: false
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: BusinessDomain
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
