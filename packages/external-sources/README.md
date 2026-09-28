# moex-external-sources

Adapters implementing the modeling-kernel `SpecificationSource` port (ADR-017).

- **Ontology (FIBO):** Mirror → seed → ROBOT extract → pin module
- **Git artifacts (OpenAPI / AsyncAPI / ODCM):** pin tag/commit → copy into `spec/`

Kernel holds only the Protocol; this package owns HTTP/git/ROBOT I/O.
