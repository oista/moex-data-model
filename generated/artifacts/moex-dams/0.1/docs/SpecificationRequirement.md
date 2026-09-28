---
search:
  boost: 10.0
---

# Class: SpecificationRequirement 


_Нормативное требование к модели, соответствующей reference specification (каталог для уровня ИТ-решения и др.)._



<div data-search-exclude markdown="1">



URI: [dams:SpecificationRequirement](https://data.moex.com/dams/SpecificationRequirement)





```mermaid
 classDiagram
    class SpecificationRequirement
    click SpecificationRequirement href "../SpecificationRequirement/"
      ModelElement <|-- SpecificationRequirement
        click ModelElement href "../ModelElement/"
      
      SpecificationRequirement : aliases
        
      SpecificationRequirement : code
        
      SpecificationRequirement : deprecated_by_ref
        
      SpecificationRequirement : description
        
      SpecificationRequirement : element_id
        
      SpecificationRequirement : formal_checks
        
          
    
        
        
        SpecificationRequirement --> "1..*" FormalCheck : formal_checks
        click FormalCheck href "../FormalCheck/"
    

        
      SpecificationRequirement : glossary_term_refs
        
          
    
        
        
        SpecificationRequirement --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm/"
    

        
      SpecificationRequirement : lifecycle_status
        
          
    
        
        
        SpecificationRequirement --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum/"
    

        
      SpecificationRequirement : name
        
      SpecificationRequirement : requirement_level
        
          
    
        
        
        SpecificationRequirement --> "1" RequirementLevelEnum : requirement_level
        click RequirementLevelEnum href "../RequirementLevelEnum/"
    

        
      SpecificationRequirement : requirement_section
        
          
    
        
        
        SpecificationRequirement --> "1" RequirementSectionEnum : requirement_section
        click RequirementSectionEnum href "../RequirementSectionEnum/"
    

        
      SpecificationRequirement : statement
        
      SpecificationRequirement : tags
        
      SpecificationRequirement : title
        
      SpecificationRequirement : valid_from
        
      SpecificationRequirement : valid_to
        
      
```





## Inheritance
* [ModelElement](ModelElement.md) [ [HasLifecycle](HasLifecycle.md)]
    * **SpecificationRequirement**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [code](code.md) | 1 <br/> [String](String.md) |  | direct |
| [requirement_level](requirement_level.md) | 1 <br/> [RequirementLevelEnum](RequirementLevelEnum.md) |  | direct |
| [requirement_section](requirement_section.md) | 1 <br/> [RequirementSectionEnum](RequirementSectionEnum.md) |  | direct |
| [statement](statement.md) | 1 <br/> [String](String.md) | Развёрнутая формулировка требования на понятном языке | direct |
| [formal_checks](formal_checks.md) | 1..* <br/> [FormalCheck](FormalCheck.md) |  | direct |
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
| [RequirementCatalog](RequirementCatalog.md) | [requirements](requirements.md) | range | [SpecificationRequirement](SpecificationRequirement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:SpecificationRequirement |
| native | dams:SpecificationRequirement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: SpecificationRequirement
description: Нормативное требование к модели, соответствующей reference specification
  (каталог для уровня ИТ-решения и др.).
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
slots:
- code
- requirement_level
- requirement_section
- statement
- formal_checks

```
</details>

### Induced

<details>
```yaml
name: SpecificationRequirement
description: Нормативное требование к модели, соответствующей reference specification
  (каталог для уровня ИТ-решения и др.).
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
is_a: ModelElement
attributes:
  code:
    name: code
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - SpecificationRequirement
    range: string
    required: true
    pattern: ^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$
  requirement_level:
    name: requirement_level
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - SpecificationRequirement
    range: RequirementLevelEnum
    required: true
  requirement_section:
    name: requirement_section
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - SpecificationRequirement
    range: RequirementSectionEnum
    required: true
  statement:
    name: statement
    description: Развёрнутая формулировка требования на понятном языке.
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - SpecificationRequirement
    range: string
    required: true
  formal_checks:
    name: formal_checks
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - SpecificationRequirement
    range: FormalCheck
    multivalued: true
    inlined: true
    inlined_as_list: true
    minimum_cardinality: 1
  element_id:
    name: element_id
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    identifier: true
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: uriorcurie
    required: true
  name:
    name: name
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    - RequirementCatalog
    range: string
    required: true
  title:
    name: title
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: string
  description:
    name: description
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: string
    required: true
  aliases:
    name: aliases
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  glossary_term_refs:
    name: glossary_term_refs
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: GlossaryTerm
    multivalued: true
    inlined: false
  tags:
    name: tags
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - ModelElement
    range: string
    multivalued: true
  lifecycle_status:
    name: lifecycle_status
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
    domain_of:
    - HasLifecycle
    range: LifecycleStatusEnum
    required: true
  valid_from:
    name: valid_from
    from_schema: https://data.moex.com/dams/v0.1
    rank: 1000
    owner: SpecificationRequirement
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
    owner: SpecificationRequirement
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
    owner: SpecificationRequirement
    domain_of:
    - HasLifecycle
    range: uriorcurie

```
</details></div>
