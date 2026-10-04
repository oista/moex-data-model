---
id: trading-platform:adr:001
title: Demo vertical slice
date: 2026-10-04
status: accepted
model_revision: "1.0.0"
change_class: modeling
affects: []
supersedes: []
---

# Demo vertical slice

## Context

The first published DAMS solution needed a small, reviewable body that the
viewer and conformance pipeline could project.

## Decision

Use `trading-platform` as the demo implementation: one `ModelPackage` covering
conceptual / logical / physical layers and a vertical-slice publication.

## Consequences

Consumers (including agents) must treat the package as illustrative. Expanding
scope belongs in later model revisions, each with its own decision record when
the change is breaking or structural.
