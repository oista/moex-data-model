


```mermaid
 classDiagram
    class ClassificationAssignment
    click ClassificationAssignment href "../ClassificationAssignment"
      GovernanceAssignment <|-- ClassificationAssignment
        click GovernanceAssignment href "../GovernanceAssignment"
      
      ClassificationAssignment : approval_status
        
          
    
        
        
        ClassificationAssignment --> "0..1" ApprovalStatusEnum : approval_status
        click ApprovalStatusEnum href "../ApprovalStatusEnum"
    

        
      ClassificationAssignment : approved_at
        
      ClassificationAssignment : approved_by_ref
        
          
    
        
        
        ClassificationAssignment --> "0..1" Role : approved_by_ref
        click Role href "../Role"
    

        
      ClassificationAssignment : assignment_id
        
      ClassificationAssignment : assignment_scope
        
          
    
        
        
        ClassificationAssignment --> "1" AssignmentScopeEnum : assignment_scope
        click AssignmentScopeEnum href "../AssignmentScopeEnum"
    

        
      ClassificationAssignment : classification_rationale
        
      ClassificationAssignment : classification_source
        
      ClassificationAssignment : classification_term_ref
        
          
    
        
        
        ClassificationAssignment --> "0..1" DataClassificationTerm : classification_term_ref
        click DataClassificationTerm href "../DataClassificationTerm"
    

        
      ClassificationAssignment : evidence_refs
        
      ClassificationAssignment : governance_classification
        
          
    
        
        
        ClassificationAssignment --> "0..1" GovernanceClassificationEnum : governance_classification
        click GovernanceClassificationEnum href "../GovernanceClassificationEnum"
    

        
      ClassificationAssignment : source_artifact_ref
        
      ClassificationAssignment : target_element_ref
        
      ClassificationAssignment : valid_from
        
      ClassificationAssignment : valid_to
        
      
```
