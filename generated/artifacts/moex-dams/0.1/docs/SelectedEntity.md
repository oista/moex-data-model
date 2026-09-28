---
search:
  boost: 10.0
---

# Class: SelectedEntity 


_Выбранная для интеграции логическая сущность._



<div data-search-exclude markdown="1">



URI: [dams:SelectedEntity](https://data.moex.com/dams/SelectedEntity)





```mermaid
 classDiagram
    class SelectedEntity
    click SelectedEntity href "../SelectedEntity/"
      ModelElement <|-- SelectedEntity
        click ModelElement href "../ModelElement/"
      
      SelectedEntity : aliases
        
      SelectedEntity : deprecated_by_ref
        
      SelectedEntity : description
        
      SelectedEntity : element_id
        
      SelectedEntity : glossary_term_refs
        
          
    
        
        
        SelectedEntity --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      SelectedEntity : lifecycle_status
        
          
    
        
        
        SelectedEntity --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      SelectedEntity : logical_entity_ref
        
          
    
        
        
        SelectedEntity --> "1" LogicalEntity : logical_entity_ref
        click LogicalEntity href "../LogicalEntity/"
    

        
      SelectedEntity : name
        
      SelectedEntity : physical_object_refs
        
          
    
        
        
        SelectedEntity --> "1..*" PhysicalObject : physical_object_refs
        click PhysicalObject href "../PhysicalObject/"
    

        
      SelectedEntity : selected_attributes
        
          
    
        
        
        SelectedEntity --> "1..*" SelectedAttribute : selected_attributes
        click SelectedAttribute href "../SelectedAttribute/"
    

        
      SelectedEntity : tags
        
      SelectedEntity : title
        
      SelectedEntity : valid_from
        
      SelectedEntity : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **SelectedEntity**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [logical_entity_ref](logical_entity_ref.md) | 1 <br/> [LogicalEntity](LogicalEntity.md) |  | direct |
| [selected_attributes](selected_attributes.md) | 1..* <br/> [SelectedAttribute](SelectedAttribute.md) |  | direct |
| [physical_object_refs](physical_object_refs.md) | 1..* <br/> [PhysicalObject](PhysicalObject.md) |  | direct |
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
| [ModelSelection](ModelSelection.md) | [selected_entities](selected_entities.md) | range | [SelectedEntity](SelectedEntity.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:SelectedEntity |
| native | dams:SelectedEntity |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: SelectedEntity
description: Выбранная для интеграции логическая сущность.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
slots:
- logical_entity_ref
- selected_attributes
- physical_object_refs

```
</details>

### Induced

<details>
```yaml
name: SelectedEntity
description: Выбранная для интеграции логическая сущность.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
attributes:
  logical_entity_ref:
    name: logical_entity_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - DataFlowEntityBinding
    - SelectedEntity
    range: LogicalEntity
    required: true
    inlined: false
  selected_attributes:
    name: selected_attributes
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - SelectedEntity
    range: SelectedAttribute
    multivalued: true
    inlined: true
    inlined_as_list: true
    minimum_cardinality: 1
  physical_object_refs:
    name: physical_object_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - DataFlowEntityBinding
    - SelectedEntity
    range: PhysicalObject
    multivalued: true
    inlined: false
    minimum_cardinality: 1
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SelectedEntity
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
    owner: SelectedEntity
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
    owner: SelectedEntity
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
