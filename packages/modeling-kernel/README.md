# moex-modeling-kernel

Python envelopes and ports for the MOEX modeling kernel
([`docs/architecture/modeling-kernel.yaml`](../../docs/architecture/modeling-kernel.yaml)).

Typed standard bodies live in provider packages (`standard-linkml`, …), not here.

## Install

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel[dev]"
```

## Public surface

- Coordinates: `ModelingStandard`, `ReferenceSpecification`, `SpecificationImplementation`
- Conformance: `Diagnostic`, `ConformanceAssessment`, `ConformanceReport`
- Registry: `ModelUniverse`, `TypedRelation`
- Protocol: `StandardProvider[TSpecBody, TImplBody, TElement]` with **distinct** body type parameters
- Ports: `SchemaRepository`, `MappingProvider`, `ImportDraftEngine` (Stage 7)

Fitness test (must stay green once this package exists):

```text
tests/architecture/test_public_apis.py::test_standard_provider_has_distinct_body_types
```

## Tests

```powershell
py -3.14 -m pytest packages/modeling-kernel/tests tests/architecture -q
```
