


```mermaid
 classDiagram
    class HasPolicyBindings
    click HasPolicyBindings href "../HasPolicyBindings"
      HasPolicyBindings <|-- ModelPackage
        click ModelPackage href "../ModelPackage"
      HasPolicyBindings <|-- LogicalEntity
        click LogicalEntity href "../LogicalEntity"
      HasPolicyBindings <|-- LogicalAttribute
        click LogicalAttribute href "../LogicalAttribute"
      HasPolicyBindings <|-- PhysicalField
        click PhysicalField href "../PhysicalField"
      HasPolicyBindings <|-- TechnicalAsset
        click TechnicalAsset href "../TechnicalAsset"
      HasPolicyBindings <|-- Metric
        click Metric href "../Metric"
      
      HasPolicyBindings : policy_refs
        
          
    
        
        
        HasPolicyBindings --> "*" Policy : policy_refs
        click Policy href "../Policy"
    

        
      
```
