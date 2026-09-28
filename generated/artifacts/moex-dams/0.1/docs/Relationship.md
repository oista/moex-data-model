---
search:
  boost: 10.0
---

# Class: Relationship 


_Именованная связь между логическими или концептуальными сущностями._



<div data-search-exclude markdown="1">



URI: [dams:Relationship](https://data.moex.com/dams/Relationship)





```mermaid
 classDiagram
    class Relationship
    click Relationship href "../Relationship/"
      ModelElement <|-- Relationship
        click ModelElement href "../ModelElement/"
      
      Relationship : aliases
        
      Relationship : associative
        
      Relationship : deprecated_by_ref
        
      Relationship : description
        
      Relationship : element_id
        
      Relationship : glossary_term_refs
        
          
    
        
        
        Relationship --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      Relationship : identifying
        
      Relationship : lifecycle_status
        
          
    
        
        
        Relationship --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      Relationship : name
        
      Relationship : source_entity_ref
        
      Relationship : source_max_cardinality
        
      Relationship : source_min_cardinality
        
      Relationship : source_role
        
      Relationship : tags
        
      Relationship : target_entity_ref
        
      Relationship : target_max_cardinality
        
      Relationship : target_min_cardinality
        
      Relationship : target_role
        
      Relationship : title
        
      Relationship : valid_from
        
      Relationship : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **Relationship**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [source_entity_ref](source_entity_ref.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | direct |
| [target_entity_ref](target_entity_ref.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | direct |
| [source_role](source_role.md) | 0..1 <br/> [String](String.md) |  | direct |
| [target_role](target_role.md) | 0..1 <br/> [String](String.md) |  | direct |
| [source_min_cardinality](source_min_cardinality.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [source_max_cardinality](source_max_cardinality.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [target_min_cardinality](target_min_cardinality.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [target_max_cardinality](target_max_cardinality.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [identifying](identifying.md) | 0..1 <br/> [Boolean](Boolean.md) |  | direct |
| [associative](associative.md) | 0..1 <br/> [Boolean](Boolean.md) |  | direct |
| [element_id](element_id.md) | 1 <br/> [Uriorcurie](Uriorcurie.md) |  | [ModelElement](ModelElement.md) |
| [name](name.md) | 1 <br/> [String](String.md) |  | [ModelElement](ModelElement.md) |
| [title](title.md) | 0..1 <br/> [String](String.md) |  | [ModelElement](ModelElement.md) |
| [description](description.md) | 1 <br/> [String](String.md) |  | [ModelElement](ModelElement.md) |
| [aliases](aliases.md) | * <br/> [String](String.md) |  | [ModelElement](ModelElement.md) |
| [glossary_term_refs](glossary_term_refs.md) | * <br/> [GlossaryTerm](GlossaryTerm.md) |  | [ModelElement](ModelElement.md) |
| [tags](tags.md) | * <br/> [String](String.md) |  | [ModelElement](ModelElement.md) |
| [lifecycle_status](lifecycle_status.md) | 1 <br/> [LifecycleStatusEnum](LifecycleStatusEnum.md) |  | [HasLifecycle](HasLifecycle.md) |
| [valid_from](valid_from.md) | 0..1 <br/> [Datetime](Datetime.md) |  | [HasLifecycle](HasLifecycle.md) |
| [valid_to](valid_to.md) | 0..1 <br/> [Datetime](Datetime.md) |  | [HasLifecycle](HasLifecycle.md) |
| [deprecated_by_ref](deprecated_by_ref.md) | 0..1 <br/> [Uriorcurie](Uriorcurie.md) |  | [HasLifecycle](HasLifecycle.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ModelPackage](ModelPackage.md) | [relationships](relationships.md) | range | [Relationship](Relationship.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:Relationship |
| native | dams:Relationship |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Relationship
description: Именованная связь между логическими или концептуальными сущностями.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
slots:
- source_entity_ref
- target_entity_ref
- source_role
- target_role
- source_min_cardinality
- source_max_cardinality
- target_min_cardinality
- target_max_cardinality
- identifying
- associative

```
</details>

### Induced

<details>
```yaml
name: Relationship
description: Именованная связь между логическими или концептуальными сущностями.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
attributes:
  source_entity_ref:
    name: source_entity_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: uriorcurie
    required: true
  target_entity_ref:
    name: target_entity_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: uriorcurie
    required: true
  source_role:
    name: source_role
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: string
  target_role:
    name: target_role
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: string
  source_min_cardinality:
    name: source_min_cardinality
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: integer
    minimum_value: 0
  source_max_cardinality:
    name: source_max_cardinality
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: integer
    minimum_value: 1
  target_min_cardinality:
    name: target_min_cardinality
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: integer
    minimum_value: 0
  target_max_cardinality:
    name: target_max_cardinality
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: integer
    minimum_value: 1
  identifying:
    name: identifying
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: boolean
  associative:
    name: associative
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - Relationship
    range: boolean
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: Relationship
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ClassificationAssignment
    - PolicyBinding
    - HasLifecycle
    - Mapping
    range: datetime
  valid_to:
    name: valid_to
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - ClassificationAssignment
    - PolicyBinding
    - HasLifecycle
    - Mapping
    range: datetime
  deprecated_by_ref:
    name: deprecated_by_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Relationship
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
