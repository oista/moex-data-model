


```mermaid
 classDiagram
    class RequirementCatalog
    click RequirementCatalog href "../RequirementCatalog"
      RequirementCatalog : catalog_id
        
      RequirementCatalog : name
        
      RequirementCatalog : requirements
        
          
    
        
        
        RequirementCatalog --> "*" SpecificationRequirement : requirements
        click SpecificationRequirement href "../SpecificationRequirement"
    

        
      
```
