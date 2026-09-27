---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-001: LinkML YAML — канонический authoring format для DAMS

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)

## Context

Нужно зафиксировать, какой текст является авторским источником для MOEX DAMS и экземпляров решений (trading-solution и т.п.). В экосистеме LinkML рядом живут JSON Schema, Pydantic, DBML, RDF/OWL, HTML viewer.

MODELING_ARCHITECTURE запрещает считать один формализм каноном **всей** мультиформальной платформы: OpenAPI и OWL — отдельные `ModelingStandard`.

## Decision

Для **DAMS-активов и LinkML toolchain** канонический authoring format — **LinkML YAML** (схемы в `model_src/schemas/`, instances как `ModelPackage`).

JSON Schema, Pydantic, DBML, RDF/OWL, SHACL, documentation и Publication Viewer — **производные** (`GENERATED_FROM` / read models). Правка производного формата не меняет опубликованный YAML напрямую: только controlled patch → validation → запись в канон.

ADR-001 **не** утверждает «вся платформа = LinkML». Другие стандарты имеют свои typed bodies в provider-пакетах.

## Consequences

- Редактирование и review идут по YAML (и по semantic diff над ним).
- `generated/` и `viewer/dist` не source of truth.
- Новый standard (OpenAPI, OWL) не требует, чтобы его канон был YAML LinkML.

## Alternatives

| Alternative | Почему нет |
|---|---|
| JSON Schema как канон | теряет LinkML constructs (mixins, rules, induced slots) |
| drawDB/DBML как канон | см. ADR-006 |
| OWL как канон экземпляров | см. ADR-010 |
| Один канон на всю платформу | ломает роли standard / specification / implementation |

## Related

- [linkml_architecture.md](../architecture/linkml_architecture.md) — Workbench toolchain
- [viewer-decisions.md](../architecture/viewer-decisions.md) — viewer не канон
- ADR-006, ADR-007, ADR-010, ADR-011
