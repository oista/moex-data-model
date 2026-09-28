---
search:
  boost: 10.0
---

# Class: OrganizationUnit 


_Организационное подразделение._



<div data-search-exclude markdown="1">



URI: [dams:OrganizationUnit](https://data.moex.com/dams/OrganizationUnit)





```mermaid
 classDiagram
    class OrganizationUnit
    click OrganizationUnit href "../OrganizationUnit/"
      RegistryEntry <|-- OrganizationUnit
        click RegistryEntry href "../RegistryEntry/"
      
      OrganizationUnit : master_system
        
      OrganizationUnit : registry_description
        
      OrganizationUnit : registry_id
        
      OrganizationUnit : registry_name
        
      OrganizationUnit : registry_status
        
          
    
        
        
        OrganizationUnit --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      OrganizationUnit : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **OrganizationUnit**


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
| [HasOwnership](HasOwnership.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [ModelPackage](ModelPackage.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [DomainContext](DomainContext.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [ConceptualEntity](ConceptualEntity.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [LogicalEntity](LogicalEntity.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [PhysicalObject](PhysicalObject.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [DataFlow](DataFlow.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [DataModelBinding](DataModelBinding.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |
| [Metric](Metric.md) | [owning_unit_ref](owning_unit_ref.md) | range | [OrganizationUnit](OrganizationUnit.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:OrganizationUnit |
| native | dams:OrganizationUnit |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: OrganizationUnit
description: Организационное подразделение.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: OrganizationUnit
description: Организационное подразделение.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: OrganizationUnit
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
