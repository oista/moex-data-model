


```mermaid
 classDiagram
    class HasLocation
    click HasLocation href "../HasLocation"
      HasLocation <|-- DataCarrier
        click DataCarrier href "../DataCarrier"
      HasLocation <|-- AccessPoint
        click AccessPoint href "../AccessPoint"
      
      HasLocation : location_uri
        
      HasLocation : region
        
      
```
