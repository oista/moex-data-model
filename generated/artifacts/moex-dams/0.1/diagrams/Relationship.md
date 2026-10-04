


```mermaid
 classDiagram
    class Relationship
    click Relationship href "../Relationship"
      ModelElement <|-- Relationship
        click ModelElement href "../ModelElement"
      
      Relationship : aliases
        
      Relationship : associative
        
      Relationship : cardinality_rationale
        
      Relationship : deprecated_by_ref
        
      Relationship : description
        
      Relationship : element_id
        
      Relationship : glossary_term_refs
        
          
    
        
        
        Relationship --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm"
    

        
      Relationship : identifying
        
      Relationship : lifecycle_status
        
          
    
        
        
        Relationship --> "1" LifecycleStatusEnum : lifecycle_status
        click LifecycleStatusEnum href "../LifecycleStatusEnum"
    

        
      Relationship : name
        
      Relationship : relation_term_ref
        
          
    
        
        
        Relationship --> "0..1" RelationTerm : relation_term_ref
        click RelationTerm href "../RelationTerm"
    

        
      Relationship : relationship_kind
        
          
    
        
        
        Relationship --> "0..1" RelationshipKindEnum : relationship_kind
        click RelationshipKindEnum href "../RelationshipKindEnum"
    

        
      Relationship : source_entity_ref
        
      Relationship : source_max_cardinality
        
      Relationship : source_min_cardinality
        
      Relationship : source_role
        
      Relationship : tags
        
      Relationship : target_entity_ref
        
      Relationship : target_max_cardinality
        
      Relationship : target_min_cardinality
        
      Relationship : target_role
        
      Relationship : term_direction
        
          
    
        
        
        Relationship --> "0..1" TermDirectionEnum : term_direction
        click TermDirectionEnum href "../TermDirectionEnum"
    

        
      Relationship : title
        
      Relationship : valid_from
        
      Relationship : valid_to
        
      
```
