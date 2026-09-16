


```mermaid
 classDiagram
    class DataFlow
    click DataFlow href "../DataFlow"
      HasOwnership <|-- DataFlow
        click HasOwnership href "../HasOwnership"
      HasLifecycle <|-- DataFlow
        click HasLifecycle href "../HasLifecycle"
      ModelElement <|-- DataFlow
        click ModelElement href "../ModelElement"
      
      DataFlow : aliases
        
      DataFlow : contract_ref
        
          
    
        
        
        DataFlow --> "0..1" DataContractReference : contract_ref
        click DataContractReference href "../DataContractReference"
    

        
      DataFlow : data_owner_ref
        
          
    
        
        
        DataFlow --> "0..1" Role : data_owner_ref
        click Role href "../Role"
    

        
      DataFlow : data_steward_ref
        
          
    
        
        
        DataFlow --> "0..1" Role : data_steward_ref
        click Role href "../Role"
    

        
      DataFlow : deprecated_by_ref
        
      DataFlow : description
        
      DataFlow : element_id
        
      DataFlow : entity_bindings
        
          
    
        
        
        DataFlow --> "*" DataFlowEntityBinding : entity_bindings
        click DataFlowEntityBinding href "../DataFlowEntityBinding"
    

        
      DataFlow : glossary_term_refs
        
          
    
        
        
        DataFlow --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm"
    

        
      DataFlow : integration_channel
        
          
    
        
        
        DataFlow --> "1" IntegrationChannelEnum : integration_channel
        click IntegrationChannelEnum href "../IntegrationChannelEnum"
    

        
      DataFlow : integration_class
        
          
    
        
        
        DataFlow --> "1" IntegrationClassEnum : integration_class
        click IntegrationClassEnum href "../IntegrationClassEnum"
    

        
      DataFlow : integration_level
        
          
    
        
        
        DataFlow --> "1" IntegrationLevelEnum : integration_level
        click IntegrationLevelEnum href "../IntegrationLevelEnum"
    

        
      DataFlow : integration_ref
        
          
    
        
        
        DataFlow --> "1" IntegrationReference : integration_ref
        click IntegrationReference href "../IntegrationReference"
    

        
      DataFlow : integration_spec_ref
        
      DataFlow : lifecycle_status
        
          
    
        
        
        DataFlow --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum"
    

        
      DataFlow : name
        
      DataFlow : owning_unit_ref
        
          
    
        
        
        DataFlow --> "0..1" OrganizationUnit : owning_unit_ref
        click OrganizationUnit href "../OrganizationUnit"
    

        
      DataFlow : source_platform_ref
        
          
    
        
        
        DataFlow --> "1" ITPlatform : source_platform_ref
        click ITPlatform href "../ITPlatform"
    

        
      DataFlow : source_solution_ref
        
          
    
        
        
        DataFlow --> "1" ITSolution : source_solution_ref
        click ITSolution href "../ITSolution"
    

        
      DataFlow : source_system_ref
        
          
    
        
        
        DataFlow --> "1" ITSystem : source_system_ref
        click ITSystem href "../ITSystem"
    

        
      DataFlow : tags
        
      DataFlow : target_platform_ref
        
          
    
        
        
        DataFlow --> "1" ITPlatform : target_platform_ref
        click ITPlatform href "../ITPlatform"
    

        
      DataFlow : target_solution_ref
        
          
    
        
        
        DataFlow --> "1" ITSolution : target_solution_ref
        click ITSolution href "../ITSolution"
    

        
      DataFlow : target_system_ref
        
          
    
        
        
        DataFlow --> "1" ITSystem : target_system_ref
        click ITSystem href "../ITSystem"
    

        
      DataFlow : title
        
      DataFlow : valid_from
        
      DataFlow : valid_to
        
      
```
