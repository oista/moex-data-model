


```mermaid
 classDiagram
    class PhysicalField
    click PhysicalField href "../PhysicalField"
      ModelElement <|-- PhysicalField
        click ModelElement href "../ModelElement"
      
      PhysicalField : aliases
        
      PhysicalField : deprecated_by_ref
        
      PhysicalField : description
        
      PhysicalField : element_id
        
      PhysicalField : glossary_term_refs
        
          
    
        
        
        PhysicalField --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm"
    

        
      PhysicalField : lifecycle_status
        
          
    
        
        
        PhysicalField --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum"
    

        
      PhysicalField : mapping_coverage_status
        
          
    
        
        
        PhysicalField --> "0..1" MappingCoverageStatusEnum : mapping_coverage_status
        click MappingCoverageStatusEnum href "../MappingCoverageStatusEnum"
    

        
      PhysicalField : mapping_rationale
        
      PhysicalField : name
        
      PhysicalField : native_name
        
      PhysicalField : native_type
        
      PhysicalField : ordinal_position
        
      PhysicalField : physical_object_ref
        
          
    
        
        
        PhysicalField --> "1" PhysicalObject : physical_object_ref
        click PhysicalObject href "../PhysicalObject"
    

        
      PhysicalField : required
        
      PhysicalField : schema_path
        
      PhysicalField : tags
        
      PhysicalField : title
        
      PhysicalField : valid_from
        
      PhysicalField : valid_to
        
      
```
