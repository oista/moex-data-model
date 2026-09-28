---
search:
  boost: 10.0
---

# Class: DataClassificationTerm 


_Специальная категория чувствительности или регулирования, например ПДн или инсайдерская информация._



<div data-search-exclude markdown="1">



URI: [dams:DataClassificationTerm](https://data.moex.com/dams/DataClassificationTerm)





```mermaid
 classDiagram
    class DataClassificationTerm
    click DataClassificationTerm href "../DataClassificationTerm/"
      RegistryEntry <|-- DataClassificationTerm
        click RegistryEntry href "../RegistryEntry/"
      
      DataClassificationTerm : master_system
        
      DataClassificationTerm : registry_description
        
      DataClassificationTerm : registry_id
        
      DataClassificationTerm : registry_name
        
      DataClassificationTerm : registry_status
        
          
    
        
        
        DataClassificationTerm --> "1" LifecycleStatusEnum : registry_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      DataClassificationTerm : source_uri
        
      
```





## Inheritance
* [RegistryEntry](RegistryEntry.md)
    * **DataClassificationTerm**


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
| [ClassificationAssignment](ClassificationAssignment.md) | [classification_term_ref](classification_term_ref.md) | range | [DataClassificationTerm](DataClassificationTerm.md) |
| [HasGovernanceClassification](HasGovernanceClassification.md) | [sensitivity_term_refs](sensitivity_term_refs.md) | range | [DataClassificationTerm](DataClassificationTerm.md) |
| [LogicalEntity](LogicalEntity.md) | [sensitivity_term_refs](sensitivity_term_refs.md) | range | [DataClassificationTerm](DataClassificationTerm.md) |
| [LogicalAttribute](LogicalAttribute.md) | [sensitivity_term_refs](sensitivity_term_refs.md) | range | [DataClassificationTerm](DataClassificationTerm.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:DataClassificationTerm |
| native | dams:DataClassificationTerm |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DataClassificationTerm
description: Специальная категория чувствительности или регулирования, например ПДн
  или инсайдерская информация.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry

```
</details>

### Induced

<details>
```yaml
name: DataClassificationTerm
description: Специальная категория чувствительности или регулирования, например ПДн
  или инсайдерская информация.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: RegistryEntry
attributes:
  registry_id:
    name: registry_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: uriorcurie
    required: true
  registry_name:
    name: registry_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: string
    required: true
  registry_description:
    name: registry_description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: string
  master_system:
    name: master_system
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: string
    required: true
  source_uri:
    name: source_uri
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: uri
  registry_status:
    name: registry_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataClassificationTerm
    domain_of:
    - RegistryEntry
    range: LifecycleStatusEnum
    required: true

```
</details></div>
