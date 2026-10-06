


```mermaid
 classDiagram
    class DescribedElement
    click DescribedElement href "../DescribedElement"
      DescribedElement <|-- HasDefinition
        click HasDefinition href "../HasDefinition"
      DescribedElement <|-- ModelElement
        click ModelElement href "../ModelElement"
      DescribedElement <|-- EmbeddedElement
        click EmbeddedElement href "../EmbeddedElement"
      
      DescribedElement : description
        
      
```
