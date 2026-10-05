# Ontology SHACL fixtures (Stage 8)

Minimal `ModelPackage` YAML used by `make ontology-check` / `test_pyshacl_instances.py`.

- `valid-model-package.yaml` — dumped via `RDFLibDumper`, conforms to `moex-dams.shacl.ttl`.
- Invalid cases are produced in tests by removing required triples after dump (LinkML loaders reject incomplete YAML).

See [ADR-030](../../../../../../docs/adr/ADR-030-dams-uri-and-prefix-policy.md).
