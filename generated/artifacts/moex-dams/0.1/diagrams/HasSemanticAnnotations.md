


```mermaid
 classDiagram
    class HasSemanticAnnotations
    click HasSemanticAnnotations href "../HasSemanticAnnotations"
      HasSemanticAnnotations <|-- ModelElement
        click ModelElement href "../ModelElement"
      
      HasSemanticAnnotations : glossary_term_refs
        
          
    
        
        
        HasSemanticAnnotations --> "*" GlossaryTerm : glossary_term_refs
        click GlossaryTerm href "../GlossaryTerm"
    

        
      HasSemanticAnnotations : tags
        
      
```
