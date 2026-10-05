


```mermaid
 classDiagram
    class SpecificationRequirement
    click SpecificationRequirement href "../SpecificationRequirement"
      ModelElement <|-- SpecificationRequirement
        click ModelElement href "../ModelElement"
      
      SpecificationRequirement : aliases
        
      SpecificationRequirement : applies_to
        
          
    
        
        
        SpecificationRequirement --> "0..1" RequirementApplicability : applies_to
        click RequirementApplicability href "../RequirementApplicability"
    

        
      SpecificationRequirement : code
        
      SpecificationRequirement : deprecated_by_ref
        
      SpecificationRequirement : description
        
      SpecificationRequirement : element_id
        
      SpecificationRequirement : formal_checks
        
          
    
        
        
        SpecificationRequirement --> "1..*" FormalCheck : formal_checks
        click FormalCheck href "../FormalCheck"
    

        
      SpecificationRequirement : glossary_term_refs
        
          
    
        
        
        SpecificationRequirement --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm"
    

        
      SpecificationRequirement : implementation_status
        
          
    
        
        
        SpecificationRequirement --> "0..1" RequirementImplementationStatus : implementation_status
        click RequirementImplementationStatus href "../RequirementImplementationStatus"
    

        
      SpecificationRequirement : lifecycle_status
        
          
    
        
        
        SpecificationRequirement --> "1" RequirementLifecycleStatus : lifecycle_status
        click RequirementLifecycleStatus href "../RequirementLifecycleStatus"
    

        
      SpecificationRequirement : name
        
      SpecificationRequirement : requirement_level
        
          
    
        
        
        SpecificationRequirement --> "1" RequirementLevelEnum : requirement_level
        click RequirementLevelEnum href "../RequirementLevelEnum"
    

        
      SpecificationRequirement : requirement_section
        
          
    
        
        
        SpecificationRequirement --> "1" RequirementSectionEnum : requirement_section
        click RequirementSectionEnum href "../RequirementSectionEnum"
    

        
      SpecificationRequirement : statement
        
      SpecificationRequirement : superseded_by
        
          
    
        
        
        SpecificationRequirement --> "0..1" SpecificationRequirement : superseded_by
        click SpecificationRequirement href "../SpecificationRequirement"
    

        
      SpecificationRequirement : tags
        
      SpecificationRequirement : title
        
      SpecificationRequirement : valid_from
        
      SpecificationRequirement : valid_to
        
      
```
