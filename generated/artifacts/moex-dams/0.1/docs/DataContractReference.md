---
search:
  boost: 10.0
---

# Class: DataContractReference 


_Ссылка на дата-контракт в корпоративном дата-каталоге._



<div data-search-exclude markdown="1">



URI: [dams:DataContractReference](https://data.moex.com/dams/DataContractReference)





```mermaid
 classDiagram
    class DataContractReference
    click DataContractReference href "../DataContractReference/"
      RegistryEntry <|-- DataContractReference
        click RegistryEntry href "../RegistryEntry/"
      
      DataContractReference : master_system
        
      DataContractReference : registry_description
        
      DataContractReference : registry_id
        
      DataContractReference : registry_name
        
      DataContractReference : registry_status
        
          
    
        
        
        DataContractReference --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      DataContractReference : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **DataContractReference**


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
| [DataFlow](DataFlow.md) | [contract_ref](contract_ref.md) | range | [DataContractReference](DataContractReference.md) |
| [DataModelBinding](DataModelBinding.md) | [contract_ref](contract_ref.md) | range | [DataContractReference](DataContractReference.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:DataContractReference |
| native | dams:DataContractReference |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DataContractReference
description: Ссылка на дата-контракт в корпоративном дата-каталоге.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: DataContractReference
description: Ссылка на дата-контракт в корпоративном дата-каталоге.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataContractReference
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
