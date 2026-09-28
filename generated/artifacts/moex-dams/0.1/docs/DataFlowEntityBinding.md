---
search:
  boost: 10.0
---

# Class: DataFlowEntityBinding 


_Связь потока с логическими сущностями, атрибутами и физическими объектами модели решения._



<div data-search-exclude markdown="1">



URI: [dams:DataFlowEntityBinding](https://data.moex.com/dams/DataFlowEntityBinding)





```mermaid
 classDiagram
    class DataFlowEntityBinding
    click DataFlowEntityBinding href "../DataFlowEntityBinding/"
      ModelElement <|-- DataFlowEntityBinding
        click ModelElement href "../ModelElement/"
      
      DataFlowEntityBinding : aliases
        
      DataFlowEntityBinding : deprecated_by_ref
        
      DataFlowEntityBinding : description
        
      DataFlowEntityBinding : direction
        
          
    
        
        
        DataFlowEntityBinding --> "1" FlowDirectionEnum : direction
        click FlowDirectionEnum href "../FlowDirectionEnum/"
    

        
      DataFlowEntityBinding : element_id
        
      DataFlowEntityBinding : flow_ref
        
          
    
        
        
        DataFlowEntityBinding --> "1" DataFlow : flow_ref
        click DataFlow href "../DataFlow/"
    

        
      DataFlowEntityBinding : glossary_term_refs
        
          
    
        
        
        DataFlowEntityBinding --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      DataFlowEntityBinding : lifecycle_status
        
          
    
        
        
        DataFlowEntityBinding --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      DataFlowEntityBinding : logical_attribute_refs
        
          
    
        
        
        DataFlowEntityBinding --> "1..*" LogicalAttribute : logical_attribute_refs
        click LogicalAttribute href "../LogicalAttribute/"
    

        
      DataFlowEntityBinding : logical_entity_ref
        
          
    
        
        
        DataFlowEntityBinding --> "1" LogicalEntity : logical_entity_ref
        click LogicalEntity href "../LogicalEntity/"
    

        
      DataFlowEntityBinding : name
        
      DataFlowEntityBinding : physical_field_refs
        
          
    
        
        
        DataFlowEntityBinding --> "*" PhysicalField : physical_field_refs
        click PhysicalField href "../PhysicalField/"
    

        
      DataFlowEntityBinding : physical_object_refs
        
          
    
        
        
        DataFlowEntityBinding --> "1..*" PhysicalObject : physical_object_refs
        click PhysicalObject href "../PhysicalObject/"
    

        
      DataFlowEntityBinding : source_model_ref
        
      DataFlowEntityBinding : tags
        
      DataFlowEntityBinding : title
        
      DataFlowEntityBinding : transformation_mapping_refs
        
          
    
        
        
        DataFlowEntityBinding --> "*" Mapping : transformation_mapping_refs
        click Mapping href "../Mapping/"
    

        
      DataFlowEntityBinding : valid_from
        
      DataFlowEntityBinding : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **DataFlowEntityBinding**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [flow_ref](flow_ref.md) | 1 <br/> [DataFlow](DataFlow.md) |  | direct |
| [source_model_ref](source_model_ref.md) | 1 <br/> [Uri](Uri.md) |  | direct |
| [logical_entity_ref](logical_entity_ref.md) | 1 <br/> [LogicalEntity](LogicalEntity.md) |  | direct |
| [logical_attribute_refs](logical_attribute_refs.md) | 1..* <br/> [LogicalAttribute](LogicalAttribute.md) |  | direct |
| [physical_object_refs](physical_object_refs.md) | 1..* <br/> [PhysicalObject](PhysicalObject.md) |  | direct |
| [physical_field_refs](physical_field_refs.md) | * <br/> [PhysicalField](PhysicalField.md) |  | direct |
| [transformation_mapping_refs](transformation_mapping_refs.md) | * <br/> [Mapping](Mapping.md) |  | direct |
| [direction](direction.md) | 1 <br/> [FlowDirectionEnum](FlowDirectionEnum.md) |  | direct |
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
| [DataFlow](DataFlow.md) | [entity_bindings](entity_bindings.md) | range | [DataFlowEntityBinding](DataFlowEntityBinding.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:DataFlowEntityBinding |
| native | dams:DataFlowEntityBinding |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DataFlowEntityBinding
description: Связь потока с логическими сущностями, атрибутами и физическими объектами
  модели решения.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
slots:
- flow_ref
- source_model_ref
- logical_entity_ref
- logical_attribute_refs
- physical_object_refs
- physical_field_refs
- transformation_mapping_refs
- direction

```
</details>

### Induced

<details>
```yaml
name: DataFlowEntityBinding
description: Связь потока с логическими сущностями, атрибутами и физическими объектами
  модели решения.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
attributes:
  flow_ref:
    name: flow_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    range: DataFlow
    required: true
    inlined: false
  source_model_ref:
    name: source_model_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    range: uri
    required: true
  logical_entity_ref:
    name: logical_entity_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    - SelectedEntity
    range: LogicalEntity
    required: true
    inlined: false
  logical_attribute_refs:
    name: logical_attribute_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    range: LogicalAttribute
    multivalued: true
    inlined: false
    minimum_cardinality: 1
  physical_object_refs:
    name: physical_object_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    - SelectedEntity
    range: PhysicalObject
    multivalued: true
    inlined: false
    minimum_cardinality: 1
  physical_field_refs:
    name: physical_field_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    - SelectedAttribute
    range: PhysicalField
    multivalued: true
    inlined: false
  transformation_mapping_refs:
    name: transformation_mapping_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - DataFlowEntityBinding
    range: Mapping
    multivalued: true
    inlined: false
  direction:
    name: direction
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - PhysicalObject
    - DataFlowEntityBinding
    range: FlowDirectionEnum
    required: true
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: DataFlowEntityBinding
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
    owner: DataFlowEntityBinding
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
    owner: DataFlowEntityBinding
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
