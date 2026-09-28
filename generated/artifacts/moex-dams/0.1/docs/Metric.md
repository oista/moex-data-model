---
search:
  boost: 10.0
---

# Class: Metric 


_Управляемое определение бизнес- или технической метрики; является опциональным аналитическим профилем._



<div data-search-exclude markdown="1">



URI: [dams:Metric](https://data.moex.com/dams/Metric)





```mermaid
 classDiagram
    class Metric
    click Metric href "../Metric/"
      HasOwnership <|-- Metric
        click HasOwnership href "../HasOwnership/"
      HasPolicyBindings <|-- Metric
        click HasPolicyBindings href "../HasPolicyBindings/"
      ModelElement <|-- Metric
        click ModelElement href "../ModelElement/"
      
      Metric : aggregation_function
        
      Metric : aliases
        
      Metric : data_owner_ref
        
          
    
        
        
        Metric --> "0..1" Role : data_owner_ref
        click Role href "../Role/"
    

        
      Metric : data_steward_ref
        
          
    
        
        
        Metric --> "0..1" Role : data_steward_ref
        click Role href "../Role/"
    

        
      Metric : deprecated_by_ref
        
      Metric : description
        
      Metric : dimension_attribute_refs
        
          
    
        
        
        Metric --> "*" LogicalAttribute : dimension_attribute_refs
        click LogicalAttribute href "../LogicalAttribute/"
    

        
      Metric : element_id
        
      Metric : filter_expression
        
      Metric : glossary_term_refs
        
          
    
        
        
        Metric --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      Metric : grain_entity_refs
        
          
    
        
        
        Metric --> "1..*" LogicalEntity : grain_entity_refs
        click LogicalEntity href "../LogicalEntity/"
    

        
      Metric : lifecycle_status
        
          
    
        
        
        Metric --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      Metric : measure_attribute_refs
        
          
    
        
        
        Metric --> "1..*" LogicalAttribute : measure_attribute_refs
        click LogicalAttribute href "../LogicalAttribute/"
    

        
      Metric : metric_expression
        
      Metric : name
        
      Metric : owning_unit_ref
        
          
    
        
        
        Metric --> "0..1" OrganizationUnit : owning_unit_ref
        click OrganizationUnit href "../OrganizationUnit/"
    

        
      Metric : policy_refs
        
          
    
        
        
        Metric --> "*" Policy : policy_refs
        click Policy href "../Policy/"
    

        
      Metric : tags
        
      Metric : title
        
      Metric : unit
        
      Metric : valid_from
        
      Metric : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **Metric** [ [HasOwnership](HasOwnership.md) [HasPolicyBindings](HasPolicyBindings.md)]


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [metric_expression](metric_expression.md) | 1 <br/> [String](String.md) |  | direct |
| [aggregation_function](aggregation_function.md) | 1 <br/> [String](String.md) |  | direct |
| [grain_entity_refs](grain_entity_refs.md) | 1..* <br/> [LogicalEntity](LogicalEntity.md) |  | direct |
| [dimension_attribute_refs](dimension_attribute_refs.md) | * <br/> [LogicalAttribute](LogicalAttribute.md) |  | direct |
| [measure_attribute_refs](measure_attribute_refs.md) | 1..* <br/> [LogicalAttribute](LogicalAttribute.md) |  | direct |
| [unit](unit.md) | 0..1 <br/> [String](String.md) |  | direct |
| [filter_expression](filter_expression.md) | 0..1 <br/> [String](String.md) |  | direct |
| [data_owner_ref](data_owner_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [data_steward_ref](data_steward_ref.md) | 0..1 <br/> [Role](Role.md) |  | [HasOwnership](HasOwnership.md) |
| [owning_unit_ref](owning_unit_ref.md) | 0..1 <br/> [OrganizationUnit](OrganizationUnit.md) |  | [HasOwnership](HasOwnership.md) |
| [policy_refs](policy_refs.md) | * <br/> [Policy](Policy.md) |  | [HasPolicyBindings](HasPolicyBindings.md) |
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
| [MOEXModelRepository](MOEXModelRepository.md) | [metrics](metrics.md) | range | [Metric](Metric.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:Metric |
| native | dams:Metric |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Metric
description: Управляемое определение бизнес- или технической метрики; является опциональным
  аналитическим профилем.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
- HasPolicyBindings
slots:
- metric_expression
- aggregation_function
- grain_entity_refs
- dimension_attribute_refs
- measure_attribute_refs
- unit
- filter_expression

```
</details>

### Induced

<details>
```yaml
name: Metric
description: Управляемое определение бизнес- или технической метрики; является опциональным
  аналитическим профилем.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
mixins:
- HasOwnership
- HasPolicyBindings
attributes:
  metric_expression:
    name: metric_expression
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    range: string
    required: true
  aggregation_function:
    name: aggregation_function
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    range: string
    required: true
  grain_entity_refs:
    name: grain_entity_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    - Dimension
    range: LogicalEntity
    multivalued: true
    inlined: false
    minimum_cardinality: 1
  dimension_attribute_refs:
    name: dimension_attribute_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    - Dimension
    range: LogicalAttribute
    multivalued: true
    inlined: false
  measure_attribute_refs:
    name: measure_attribute_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    range: LogicalAttribute
    multivalued: true
    inlined: false
    minimum_cardinality: 1
  unit:
    name: unit
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    range: string
  filter_expression:
    name: filter_expression
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - Metric
    range: string
  data_owner_ref:
    name: data_owner_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  data_steward_ref:
    name: data_steward_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - HasOwnership
    range: Role
    inlined: false
  owning_unit_ref:
    name: owning_unit_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - HasOwnership
    range: OrganizationUnit
    inlined: false
  policy_refs:
    name: policy_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - HasPolicyBindings
    range: Policy
    multivalued: true
    inlined: false
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: Metric
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: Metric
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
    owner: Metric
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
    owner: Metric
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
