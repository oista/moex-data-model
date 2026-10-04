# UML diagrams — MOEX DAMS / external alignment

**Normative source of truth:** LinkML schemas.  
UML here is illustrative (key classes, slots, and associations). Validation / publication checks are process tooling, not metamodel classes.

## Core hierarchy

```text
ModelingStandard                          (modeling-kernel.yaml)
  └── ReferenceSpecification              (e.g. MOEX DAMS 0.1)
        └── SpecificationImplementation   (envelope: profile, dams_model_level, body_ref)
              └── ModelPackage            (DAMS body; moex-core.yaml)
                    ├── implementation_scope = enterprise
                    │     └── ConceptualEntity / Relationship / …
                    └── implementation_scope = solution
                          ├── DomainContext / LogicalEntity / LogicalAttribute / Relationship
                          ├── PhysicalObject / PhysicalField
                          └── Mapping (realizes, entity_physical, field_mapping, …)
```

Roles `enterprise-conceptual` and `solution` are SpecImpl / `ModelPackage` coordinates (`dams_model_level` / `implementation_scope`), not separate LinkML classes.

## Diagrams

| File | Question | LinkML sources |
|---|---|---|
| [01-core-data-model.puml](01-core-data-model.puml) | How corporate meaning relates to solution logical/physical data? | `moex-core.yaml`, `moex-registries.yaml`, governance mixins |
| [02-solution-model-governance.puml](02-solution-model-governance.puml) | How kernel envelope, packages, registries, flows, and policy bindings fit? | `modeling-kernel.yaml`, `moex-dams.yaml`, `moex-integration.yaml`, `moex-contract-binding.yaml`, `moex-governance.yaml` |
| [03-external-semantics.puml](03-external-semantics.puml) | How external scope/selection aligns to conceptual entities? | `moex-external-alignment.yaml` + DAMS bridge |
| [all_model_modules.puml](all_model_modules.puml) | Slim overview of kernel + DAMS + registries + external-alignment | all of the above |

## Explicit non-classes

Not LinkML classes (do not reintroduce in UML):

- `IdentifiedElement` / `GovernedElement` — use `ModelElement` + mixins
- `ConceptualAttribute` / `ConceptualRelationship` / `BusinessTerm` / `ValueSet*`
- `Technology` / `NativeSchema` / `ModelElementRealization` / `Transformation` as classes
- `DataFlowEndpoint` / `DataContract` / `DataQuality*` / `DataOwner` / `DataSteward`
- `EnterpriseConceptualModel` / `SolutionDataModel` / `ExternalSourceLock` / `ExternalSemanticAlignment`
- Schema/body/publication check services — pipeline process only
