


```mermaid
 classDiagram
    class IdentifiedElement
    click IdentifiedElement href "../IdentifiedElement"
      IdentifiedElement <|-- ModelElement
        click ModelElement href "../ModelElement"
      IdentifiedElement <|-- Mapping
        click Mapping href "../Mapping"
      
      IdentifiedElement : element_id
        
      
```
