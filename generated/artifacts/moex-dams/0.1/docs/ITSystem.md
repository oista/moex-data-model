---
search:
  boost: 10.0
---

# Class: ITSystem 


_ИТ-система; мастер данных — EAM._



<div data-search-exclude markdown="1">



URI: [dams:ITSystem](https://data.moex.com/dams/ITSystem)





```mermaid
 classDiagram
    class ITSystem
    click ITSystem href "../ITSystem/"
      RegistryEntry <|-- ITSystem
        click RegistryEntry href "../RegistryEntry/"
      
      ITSystem : master_system
        
      ITSystem : registry_description
        
      ITSystem : registry_id
        
      ITSystem : registry_name
        
      ITSystem : registry_status
        
          
    
        
        
        ITSystem --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      ITSystem : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **ITSystem**


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
| [ITSolution](ITSolution.md) | [member_system_refs](member_system_refs.md) | range | [ITSystem](ITSystem.md) |
| [PhysicalObject](PhysicalObject.md) | [system_ref](system_ref.md) | range | [ITSystem](ITSystem.md) |
| [DataFlow](DataFlow.md) | [source_system_ref](source_system_ref.md) | range | [ITSystem](ITSystem.md) |
| [DataFlow](DataFlow.md) | [target_system_ref](target_system_ref.md) | range | [ITSystem](ITSystem.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:ITSystem |
| native | dams:ITSystem |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ITSystem
description: ИТ-система; мастер данных — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: ITSystem
description: ИТ-система; мастер данных — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSystem
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
