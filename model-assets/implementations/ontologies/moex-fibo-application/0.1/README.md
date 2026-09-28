# MOEX FIBO application ontology (SpecificationImplementation)

Governed OWL **application / extension ontology** for MOEX (ADR-018).  
Not a subset copy of FIBO: imports a pinned extract, adds a MOEX namespace, and bridges to DAMS.

| Layer | File | Ownership |
|---|---|---|
| Imported module | `metamodel/fibo-import-module.ttl` | Upstream slice (pin/copy from ADR-017 `external-sources/fibo`) |
| Extension | `metamodel/moex-fibo-extension.ttl` | MOEX |
| Mapping bridge | `metamodel/moex-dams-fibo-mapping.ttl` | MOEX (plus SSSOM at `transformations/mappings/dams-fibo.sssom.yaml`) |

- Envelope: `implementation.yaml` (`conforms_to` → `moex-fibo-profile`)
- Provider descriptor: `ontology-application.yaml` (`conformance_level`, `seed_ref`, artifact refs)
- Profile Spec: [moex-fibo-profile](../../../specifications/moex-fibo-profile/0.1/)
- Upstream sync: [ADR-017](../../../../../docs/adr/ADR-017-external-specification-source-sync.md)
- Decision: [ADR-018](../../../../../docs/adr/ADR-018-ontology-application-implementation.md)

The catalog stub `moex:ontology:application` is superseded by this Impl id `moex:implementation:moex-fibo-application:0.1`.
