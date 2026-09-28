# MOEX External Alignment (ADR-020)

Governance metamodel for selecting terms from external reference specifications
(FIBO, OpenAPI, AsyncAPI, ODCM, JSON Schema, …).

## Layers

| Artifact | Role |
|---|---|
| ExternalSpecification[+Version] | Registered upstream + version pin (`external-sources/…/versions/`) |
| ExternalSpecificationScope | Search/interest boundary — **not** an import |
| ExternalTermSelection | Reviewable term set, CQ, mappings, extraction plan |

## Related

- Sync: [external-sources](../../../external-sources/) (ADR-017)
- Application ontology: [moex-fibo-application](../../../implementations/ontologies/moex-fibo-application/) (ADR-018)
- Schema: [schemas/moex-external-alignment.yaml](schemas/moex-external-alignment.yaml)
- ADR: [ADR-020](../../../../docs/adr/ADR-020-external-specification-scope-and-term-selection.md)
