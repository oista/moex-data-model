


```mermaid
 classDiagram
    class HasValidity
    click HasValidity href "../HasValidity"
      HasValidity <|-- GovernanceAssignment
        click GovernanceAssignment href "../GovernanceAssignment"
      HasValidity <|-- HasLifecycle
        click HasLifecycle href "../HasLifecycle"
      
      HasValidity : valid_from
        
      HasValidity : valid_to
        
      
```
