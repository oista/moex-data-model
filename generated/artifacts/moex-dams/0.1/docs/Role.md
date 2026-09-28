---
search:
  boost: 10.0
---

# Class: Role 


_Управляемая роль владельца, стюарда, потребителя или согласующего._



<div data-search-exclude markdown="1">



URI: [dams:Role](https://data.moex.com/dams/Role)





```mermaid
 classDiagram
    class Role
    click Role href "../Role/"
      RegistryEntry <|-- Role
        click RegistryEntry href "../RegistryEntry/"
      
      Role : master_system
        
      Role : registry_description
        
      Role : registry_id
        
      Role : registry_name
        
      Role : registry_status
        
          
    
        
        
        Role --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      Role : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **Role**


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
| [HasOwnership](HasOwnership.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [HasOwnership](HasOwnership.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [HasProvenance](HasProvenance.md) | [approved_by_ref](approved_by_ref.md) | range | [Role](Role.md) |
| [ModelPackage](ModelPackage.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [ModelPackage](ModelPackage.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [DomainContext](DomainContext.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [DomainContext](DomainContext.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [ConceptualEntity](ConceptualEntity.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [ConceptualEntity](ConceptualEntity.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [LogicalEntity](LogicalEntity.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [LogicalEntity](LogicalEntity.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [PhysicalObject](PhysicalObject.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [PhysicalObject](PhysicalObject.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [Mapping](Mapping.md) | [approved_by_ref](approved_by_ref.md) | range | [Role](Role.md) |
| [DataFlow](DataFlow.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [DataFlow](DataFlow.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [DataModelBinding](DataModelBinding.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [DataModelBinding](DataModelBinding.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |
| [Metric](Metric.md) | [data_owner_ref](data_owner_ref.md) | range | [Role](Role.md) |
| [Metric](Metric.md) | [data_steward_ref](data_steward_ref.md) | range | [Role](Role.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:Role |
| native | dams:Role |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Role
description: Управляемая роль владельца, стюарда, потребителя или согласующего.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: Role
description: Управляемая роль владельца, стюарда, потребителя или согласующего.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: Role
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Role
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Role
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Role
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Role
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Role
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
