---
search:
  boost: 10.0
---

# Class: ConceptualEntity 


_Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реализации._



<div data-search-exclude markdown="1">



URI: [dams:ConceptualEntity](https://data.moex.com/dams/ConceptualEntity)





```mermaid
 classDiagram
    class ConceptualEntity
    click ConceptualEntity href "../ConceptualEntity/"
      HasOwnership <|-- ConceptualEntity
        click HasOwnership href "../HasOwnership/"
      HasBusinessClassification <|-- ConceptualEntity
        click HasBusinessClassification href "../HasBusinessClassification/"
      ModelElement <|-- ConceptualEntity
        click ModelElement href "../ModelElement/"
      
      ConceptualEntity : aliases
        
      ConceptualEntity : business_importance
        
          
    
        
        
        ConceptualEntity --> "0..1" BusinessImportanceEnum : business_importance
        click BusinessImportanceEnum href "../BusinessImportanceEnum/"
    

        
      ConceptualEntity : data_class
        
          
    
        
        
        ConceptualEntity --> "0..1" DataClassEnum : data_class
        click DataClassEnum href "../DataClassEnum/"
    

        
      ConceptualEntity : data_owner_ref
        
          
    
        
        
        ConceptualEntity --> "0..1" Role : data_owner_ref
        click Role href "../Role/"
    

        
      ConceptualEntity : data_steward_ref
        
          
    
        
        
        ConceptualEntity --> "0..1" Role : data_steward_ref
        click Role href "../Role/"
    

        
      ConceptualEntity : deprecated_by_ref
        
      ConceptualEntity : description
        
      ConceptualEntity : element_id
        
      ConceptualEntity : entity_type
        
          
    
        
        
        ConceptualEntity --> "0..1" EntityTypeEnum : entity_type
        click EntityTypeEnum href "../EntityTypeEnum/"
    

        
      ConceptualEntity : glossary_term_refs
        
          
    
        
        
        ConceptualEntity --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      ConceptualEntity : key_attribute_refs
        
      ConceptualEntity : lifecycle_status
        
          
    
        
        
        ConceptualEntity --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      ConceptualEntity : name
        
      ConceptualEntity : owning_unit_ref
        
          
    
        
        
        ConceptualEntity --> "0..1" OrganizationUnit : owning_unit_ref
        click OrganizationUnit href "../OrganizationUnit/"
    

        
      ConceptualEntity : parent_concept_ref
        
          
    
        
        
        ConceptualEntity --> "0..1" ConceptualEntity : parent_concept_ref
        click ConceptualEntity href "../ConceptualEntity/"
    

        
      ConceptualEntity : tags
        
      ConceptualEntity : title
        
      ConceptualEntity : valid_from
        
      ConceptualEntity : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **ConceptualEntity** [ [HasOwnership](HasOwnership.md) [HasBusinessClassification](HasBusinessClassification.md)]


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [parent_concept_ref](parent_concept_ref.md) | 0..1 <br/> [ConceptualEntity](ConceptualEntity.md) |  | direct |
| [key_attribute_refs](key_attribute_refs.md) | * <br/> [Uriorcurie](Uriorcurie.md) |  | direct |
| [data_owner_ref](data_owner_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [data_steward_ref](data_steward_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [owning_unit_ref](owning_unit_ref.md) | 0..1 <br/> [OrganizationUnit](OrganizationUnit.md) |  | [HasOwnership](HasOwnership.md) |
| [entity_type](entity_type.md) | 0..1 <br/> [EntityTypeEnum](EntityTypeEnum.md) |  | [HasBusinessClassification](HasBusinessClassification.md) |
| [data_class](data_class.md) | 0..1 <br/> [DataClassEnum](DataClassEnum.md) |  | [HasBusinessClassification](HasBusinessClassification.md) |
| [business_importance](business_importance.md) | 0..1 <br/> [BusinessImportanceEnum](BusinessImportanceEnum.md) |  | [HasBusinessClassification](HasBusinessClassification.md) |
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
| [ModelPackage](ModelPackage.md) | [conceptual_entities](conceptual_entities.md) | range | [ConceptualEntity](ConceptualEntity.md) |
| [ConceptualEntity](ConceptualEntity.md) | [parent_concept_ref](parent_concept_ref.md) | range | [ConceptualEntity](ConceptualEntity.md) |
| [LogicalEntity](LogicalEntity.md) | [conceptual_entity_refs](conceptual_entity_refs.md) | range | [ConceptualEntity](ConceptualEntity.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:ConceptualEntity |
| native | dams:ConceptualEntity |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ConceptualEntity
description: Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной
  реализации.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
- HasBusinessClassification
slots:
- parent_concept_ref
- key_attribute_refs

```
</details>

### Induced

<details>
```yaml
name: ConceptualEntity
description: Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной
  реализации.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
- HasBusinessClassification
attributes:
  parent_concept_ref:
    name: parent_concept_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ConceptualEntity
    range: ConceptualEntity
    inlined: false
  key_attribute_refs:
    name: key_attribute_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ConceptualEntity
    - LogicalEntity
    range: uriorcurie
    multivalued: true
  data_owner_ref:
    name: data_owner_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  data_steward_ref:
    name: data_steward_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  owning_unit_ref:
    name: owning_unit_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasOwnership
    range: OrganizationUnit
    inlined: false
  entity_type:
    name: entity_type
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasBusinessClassification
    range: EntityTypeEnum
  data_class:
    name: data_class
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasBusinessClassification
    range: DataClassEnum
  business_importance:
    name: business_importance
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasBusinessClassification
    range: BusinessImportanceEnum
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ConceptualEntity
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
    owner: ConceptualEntity
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
    owner: ConceptualEntity
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
