---
search:
  boost: 10.0
---

# Class: PhysicalField 


_Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute._



<div data-search-exclude markdown="1">



URI: [dams:PhysicalField](https://data.moex.com/dams/PhysicalField)





```mermaid
 classDiagram
    class PhysicalField
    click PhysicalField href "../PhysicalField/"
      ModelElement <|-- PhysicalField
        click ModelElement href "../ModelElement/"
      
      PhysicalField : aliases
        
      PhysicalField : deprecated_by_ref
        
      PhysicalField : description
        
      PhysicalField : element_id
        
      PhysicalField : glossary_term_refs
        
          
    
        
        
        PhysicalField --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      PhysicalField : lifecycle_status
        
          
    
        
        
        PhysicalField --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      PhysicalField : name
        
      PhysicalField : native_name
        
      PhysicalField : native_type
        
      PhysicalField : ordinal_position
        
      PhysicalField : physical_object_ref
        
          
    
        
        
        PhysicalField --> "1" PhysicalObject : physical_object_ref
        click PhysicalObject href "../PhysicalObject/"
    

        
      PhysicalField : required
        
      PhysicalField : schema_path
        
      PhysicalField : tags
        
      PhysicalField : title
        
      PhysicalField : valid_from
        
      PhysicalField : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **PhysicalField**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [physical_object_ref](physical_object_ref.md) | 1 <br/> [PhysicalObject](PhysicalObject.md) |  | direct |
| [native_name](native_name.md) | 1 <br/> [String](String.md) |  | direct |
| [native_type](native_type.md) | 1 <br/> [String](String.md) |  | direct |
| [required](required.md) | 1 <br/> [Boolean](Boolean.md) |  | direct |
| [ordinal_position](ordinal_position.md) | 0..1 <br/> [Integer](Integer.md) |  | direct |
| [schema_path](schema_path.md) | 0..1 <br/> [String](String.md) |  | direct |
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
| [PhysicalObject](PhysicalObject.md) | [physical_fields](physical_fields.md) | range | [PhysicalField](PhysicalField.md) |
| [DataFlowEntityBinding](DataFlowEntityBinding.md) | [physical_field_refs](physical_field_refs.md) | range | [PhysicalField](PhysicalField.md) |
| [SelectedAttribute](SelectedAttribute.md) | [physical_field_refs](physical_field_refs.md) | range | [PhysicalField](PhysicalField.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:PhysicalField |
| native | dams:PhysicalField |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: PhysicalField
description: Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
slots:
- physical_object_ref
- native_name
- native_type
- required
- ordinal_position
- schema_path

```
</details>

### Induced

<details>
```yaml
name: PhysicalField
description: Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
attributes:
  physical_object_ref:
    name: physical_object_ref
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - PhysicalField
    range: PhysicalObject
    required: true
    inlined: false
  native_name:
    name: native_name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - PhysicalField
    range: string
    required: true
  native_type:
    name: native_type
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - PhysicalField
    range: string
    required: true
  required:
    name: required
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - LogicalAttribute
    - PhysicalField
    range: boolean
    required: true
  ordinal_position:
    name: ordinal_position
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - PhysicalField
    range: integer
    minimum_value: 1
  schema_path:
    name: schema_path
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - PhysicalField
    range: string
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: PhysicalField
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
    owner: PhysicalField
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
    owner: PhysicalField
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
