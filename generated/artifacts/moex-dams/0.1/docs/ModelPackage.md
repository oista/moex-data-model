---
search:
  boost: 10.0
---

# Class: ModelPackage 


_Версионируемый артефакт модели данных одного ИТ-решения или корпоративной модели._



<div data-search-exclude markdown="1">



URI: [dams:ModelPackage](https://data.moex.com/dams/ModelPackage)





```mermaid
 classDiagram
    class ModelPackage
    click ModelPackage href "../ModelPackage/"
      HasOwnership <|-- ModelPackage
        click HasOwnership href "../HasOwnership/"
      ModelElement <|-- ModelPackage
        click ModelElement href "../ModelElement/"
      
      ModelPackage : aliases
        
      ModelPackage : api_version
        
      ModelPackage : conceptual_entities
        
          
    
        
        
        ModelPackage --> "*" ConceptualEntity : conceptual_entities
        click ConceptualEntity href "../ConceptualEntity/"
    

        
      ModelPackage : data_owner_ref
        
          
    
        
        
        ModelPackage --> "0..1" Role : data_owner_ref
        click Role href "../Role/"
    

        
      ModelPackage : data_steward_ref
        
          
    
        
        
        ModelPackage --> "0..1" Role : data_steward_ref
        click Role href "../Role/"
    

        
      ModelPackage : deprecated_by_ref
        
      ModelPackage : description
        
      ModelPackage : domain_contexts
        
          
    
        
        
        ModelPackage --> "*" DomainContext : domain_contexts
        click DomainContext href "../DomainContext/"
    

        
      ModelPackage : domain_refs
        
          
    
        
        
        ModelPackage --> "*" BusinessDomain : domain_refs
        click BusinessDomain href "../BusinessDomain/"
    

        
      ModelPackage : element_id
        
      ModelPackage : glossary_term_refs
        
          
    
        
        
        ModelPackage --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      ModelPackage : imports_refs
        
      ModelPackage : lifecycle_status
        
          
    
        
        
        ModelPackage --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      ModelPackage : logical_entities
        
          
    
        
        
        ModelPackage --> "*" LogicalEntity : logical_entities
        click LogicalEntity href "../LogicalEntity/"
    

        
      ModelPackage : mappings
        
          
    
        
        
        ModelPackage --> "*" Mapping : mappings
        click Mapping href "../Mapping/"
    

        
      ModelPackage : model_version
        
      ModelPackage : name
        
      ModelPackage : owning_unit_ref
        
          
    
        
        
        ModelPackage --> "0..1" OrganizationUnit : owning_unit_ref
        click OrganizationUnit href "../OrganizationUnit/"
    

        
      ModelPackage : physical_objects
        
          
    
        
        
        ModelPackage --> "*" PhysicalObject : physical_objects
        click PhysicalObject href "../PhysicalObject/"
    

        
      ModelPackage : relationships
        
          
    
        
        
        ModelPackage --> "*" Relationship : relationships
        click Relationship href "../Relationship/"
    

        
      ModelPackage : solution_ref
        
          
    
        
        
        ModelPackage --> "0..1" ITSolution : solution_ref
        click ITSolution href "../ITSolution/"
    

        
      ModelPackage : tags
        
      ModelPackage : title
        
      ModelPackage : valid_from
        
      ModelPackage : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **ModelPackage** [ [HasOwnership](HasOwnership.md)]


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [api_version](api_version.md) | 1 <br/> [String](String.md) |  | direct |
| [model_version](model_version.md) | 1 <br/> [SemVer](SemVer.md) |  | direct |
| [solution_ref](solution_ref.md) | 0..1 <br/> [ITSolution](ITSolution.md) |  | direct |
| [domain_refs](domain_refs.md) | * <br/> [BusinessDomain](BusinessDomain.md) |  | direct |
| [imports_refs](imports_refs.md) | * <br/> [Uri](Uri.md) |  | direct |
| [conceptual_entities](conceptual_entities.md) | * <br/> [ConceptualEntity](ConceptualEntity.md) |  | direct |
| [domain_contexts](domain_contexts.md) | * <br/> [DomainContext](DomainContext.md) |  | direct |
| [logical_entities](logical_entities.md) | * <br/> [LogicalEntity](LogicalEntity.md) |  | direct |
| [relationships](relationships.md) | * <br/> [Relationship](Relationship.md) |  | direct |
| [physical_objects](physical_objects.md) | * <br/> [PhysicalObject](PhysicalObject.md) |  | direct |
| [mappings](mappings.md) | * <br/> [Mapping](Mapping.md) |  | direct |
| [data_owner_ref](data_owner_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [data_steward_ref](data_steward_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [owning_unit_ref](owning_unit_ref.md) | 0..1 <br/> [OrganizationUnit](OrganizationUnit.md) |  | [HasOwnership](HasOwnership.md) |
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
| [MOEXModelRepository](MOEXModelRepository.md) | [model_packages](model_packages.md) | range | [ModelPackage](ModelPackage.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:ModelPackage |
| native | dams:ModelPackage |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ModelPackage
description: Версионируемый артефакт модели данных одного ИТ-решения или корпоративной
  модели.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
slots:
- api_version
- model_version
- solution_ref
- domain_refs
- imports_refs
- conceptual_entities
- domain_contexts
- logical_entities
- relationships
- physical_objects
- mappings

```
</details>

### Induced

<details>
```yaml
name: ModelPackage
description: Версионируемый артефакт модели данных одного ИТ-решения или корпоративной
  модели.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
attributes:
  api_version:
    name: api_version
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: string
    required: true
  model_version:
    name: model_version
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    - DataModelBinding
    range: SemVer
    required: true
  solution_ref:
    name: solution_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    - DomainContext
    - LogicalEntity
    - PhysicalObject
    range: ITSolution
    inlined: false
  domain_refs:
    name: domain_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: BusinessDomain
    multivalued: true
    inlined: false
  imports_refs:
    name: imports_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: uri
    multivalued: true
  conceptual_entities:
    name: conceptual_entities
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: ConceptualEntity
    multivalued: true
    inlined: true
    inlined_as_list: true
  domain_contexts:
    name: domain_contexts
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: DomainContext
    multivalued: true
    inlined: true
    inlined_as_list: true
  logical_entities:
    name: logical_entities
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: LogicalEntity
    multivalued: true
    inlined: true
    inlined_as_list: true
  relationships:
    name: relationships
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: Relationship
    multivalued: true
    inlined: true
    inlined_as_list: true
  physical_objects:
    name: physical_objects
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: PhysicalObject
    multivalued: true
    inlined: true
    inlined_as_list: true
  mappings:
    name: mappings
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelPackage
    range: Mapping
    multivalued: true
    inlined: true
    inlined_as_list: true
  data_owner_ref:
    name: data_owner_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  data_steward_ref:
    name: data_steward_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  owning_unit_ref:
    name: owning_unit_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - HasOwnership
    range: OrganizationUnit
    inlined: false
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: ModelPackage
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
    owner: ModelPackage
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
    owner: ModelPackage
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
