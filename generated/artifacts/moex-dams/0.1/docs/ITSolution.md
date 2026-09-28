---
search:
  boost: 10.0
---

# Class: ITSolution 


_ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM._



<div data-search-exclude markdown="1">



URI: [dams:ITSolution](https://data.moex.com/dams/ITSolution)





```mermaid
 classDiagram
    class ITSolution
    click ITSolution href "../ITSolution/"
      RegistryEntry <|-- ITSolution
        click RegistryEntry href "../RegistryEntry/"
      
      ITSolution : master_system
        
      ITSolution : member_system_refs
        
          
    
        
        
        ITSolution --> "*" ITSystem : member_system_refs
        click ITSystem href "../ITSystem/"
    

        
      ITSolution : platform_ref
        
          
    
        
        
        ITSolution --> "0..1" ITPlatform : platform_ref
        click ITPlatform href "../ITPlatform/"
    

        
      ITSolution : registry_description
        
      ITSolution : registry_id
        
      ITSolution : registry_name
        
      ITSolution : registry_status
        
          
    
        
        
        ITSolution --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      ITSolution : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **ITSolution**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [member_system_refs](member_system_refs.md) | * <br/> [ITSystem](ITSystem.md) |  | direct |
| [platform_ref](platform_ref.md) | 0..1 <br/> [ITPlatform](ITPlatform.md) |  | direct |
| [registry_id](registry_id.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_name](registry_name.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_description](registry_description.md) | 0..1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [master_system](master_system.md) | 1 <br/> [String](String.md) |  | [RegistryEntry](RegistryEntry.md) |
| [source_uri](source_uri.md) | 0..1 <br/> [Uri](Uri.md) |  | [RegistryEntry](RegistryEntry.md) |
| [registry_status](registry_status.md) | 1 <br/> [LifecycleStatusEnum](LifecycleStatusEnum.md) |  | [RegistryEntry](RegistryEntry.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ModelPackage](ModelPackage.md) | [solution_ref](solution_ref.md) | range | [ITSolution](ITSolution.md) |
| [DomainContext](DomainContext.md) | [solution_ref](solution_ref.md) | range | [ITSolution](ITSolution.md) |
| [LogicalEntity](LogicalEntity.md) | [solution_ref](solution_ref.md) | range | [ITSolution](ITSolution.md) |
| [PhysicalObject](PhysicalObject.md) | [solution_ref](solution_ref.md) | range | [ITSolution](ITSolution.md) |
| [DataFlow](DataFlow.md) | [source_solution_ref](source_solution_ref.md) | range | [ITSolution](ITSolution.md) |
| [DataFlow](DataFlow.md) | [target_solution_ref](target_solution_ref.md) | range | [ITSolution](ITSolution.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:ITSolution |
| native | dams:ITSolution |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ITSolution
description: ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных
  — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
slots:
- member_system_refs
- platform_ref

```
</details>

### Induced

<details>
```yaml
name: ITSolution
description: ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных
  — EAM.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  member_system_refs:
    name: member_system_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - ITSolution
    range: ITSystem
    multivalued: true
    inlined: false
  platform_ref:
    name: platform_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - ITSolution
    range: ITPlatform
    inlined: false
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ITSolution
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
