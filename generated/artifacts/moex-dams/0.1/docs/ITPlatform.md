---
search:
  boost: 10.0
---

# Class: ITPlatform 


_ИТ-платформа; мастер данных — EAM._



<div data-search-exclude markdown="1">



URI: [dams:ITPlatform](https://data.moex.com/dams/ITPlatform)





```mermaid
 classDiagram
    class ITPlatform
    click ITPlatform href "../ITPlatform/"
      RegistryEntry <|-- ITPlatform
        click RegistryEntry href "../RegistryEntry/"
      
      ITPlatform : master_system
        
      ITPlatform : registry_description
        
      ITPlatform : registry_id
        
      ITPlatform : registry_name
        
      ITPlatform : registry_status
        
          
    
        
        
        ITPlatform --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      ITPlatform : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **ITPlatform**


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
| [ITSolution](ITSolution.md) | [platform_ref](platform_ref.md) | range | [ITPlatform](ITPlatform.md) |
| [DataFlow](DataFlow.md) | [source_platform_ref](source_platform_ref.md) | range | [ITPlatform](ITPlatform.md) |
| [DataFlow](DataFlow.md) | [target_platform_ref](target_platform_ref.md) | range | [ITPlatform](ITPlatform.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:ITPlatform |
| native | dams:ITPlatform |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ITPlatform
description: ИТ-платформа; мастер данных — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: ITPlatform
description: ИТ-платформа; мастер данных — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITPlatform
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
