


```mermaid
 classDiagram
    class EmbeddedElement
    click EmbeddedElement href "../EmbeddedElement"
      DescribedElement <|-- EmbeddedElement
        click DescribedElement href "../DescribedElement"
      

      EmbeddedElement <|-- SchemaNode
        click SchemaNode href "../SchemaNode"
      

      EmbeddedElement : description
        
      EmbeddedElement : local_key
        
      
```
