# Consumer context

This package is a **demo** DAMS solution model (trading-platform). It illustrates
the vertical slice, not a production trading system.

## Purpose

- Show a publishable `ModelPackage` with conceptual, logical, and physical
  layers plus conformance / model-assessment.
- Give humans and agents a single entry for how to read the package.

## Non-goals

- Not a complete trading-domain model.
- Not a second glossary. Entity definitions stay on `description` / the
  definition cascade.
- Do not invent entities, slots, or mappings that are not in
  `trading-solution-model.yaml`.

## Invariants outside the schema

- Treat assessment findings as diagnostics, not as extra model elements.
- Physical objects without a logical mapping are exceptions and need rationale
  in the model YAML, not in this folder.

## For agents

1. Start here, then open accepted records under `docs/adr/` for breaking or
   modeling decisions.
2. Prefer `element_id` in the YAML over names in this prose.
3. If this page conflicts with the schema or DAMS checks, the schema wins.
