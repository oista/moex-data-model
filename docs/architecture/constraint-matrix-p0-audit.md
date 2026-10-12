---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# P0 audit close-out: executable constraint matrix

**ADR:** [ADR-045](../adr/ADR-045-executable-constraint-matrix.md) (Accepted)  
**Matrix:** [constraint-matrix.md](constraint-matrix.md)  
**Guide:** [adding-an-invariant.md](../guides/adding-an-invariant.md)

Audit P0 (инварианты без прослеживаемой машинной проверки) закрыт серией PR-C0…C5:

- L1 LinkML `rules` + negative fixtures
- L2 DAMS validators + YAML fixtures
- L3 manual SHACL (`sh:sourceShape` → INV-NNN)
- `check-constraints` в `check_all` и `publish-gate` (gate-strict)
