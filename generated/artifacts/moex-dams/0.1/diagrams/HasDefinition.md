


```mermaid
 classDiagram
    class HasDefinition
    click HasDefinition href "../HasDefinition"
      HasDefinition <|-- ConceptualEntity
        click ConceptualEntity href "../ConceptualEntity"
      HasDefinition <|-- ConceptualProperty
        click ConceptualProperty href "../ConceptualProperty"
      HasDefinition <|-- LogicalEntity
        click LogicalEntity href "../LogicalEntity"
      HasDefinition <|-- LogicalAttribute
        click LogicalAttribute href "../LogicalAttribute"
      HasDefinition <|-- RelationTerm
        click RelationTerm href "../RelationTerm"
      
      HasDefinition : definition_rationale
        
      HasDefinition : definition_source_ref
        
      HasDefinition : scoped_definitions
        
          
    
        
        
        HasDefinition --> "*" ScopedDefinition : scoped_definitions
        click ScopedDefinition href "../ScopedDefinition"
    

        
      
```
